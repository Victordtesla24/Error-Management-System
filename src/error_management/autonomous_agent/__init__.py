"""Autonomous agent for error management."""

import asyncio
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import anthropic

from src.error_management.task_manager import task_manager

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 50):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make an API call."""
        async with self.lock:
            now = time.time()
            # Remove calls older than 1 minute
            self.calls = [t for t in self.calls if now - t < 60]

            if len(self.calls) >= self.calls_per_minute:
                # Wait until we can make another call
                wait_time = 60 - (now - self.calls[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                self.calls = self.calls[1:]

            self.calls.append(now)


class ClaudeAutonomousAgent:
    def __init__(self):
        self.api_key = None
        self.client = None
        self.is_running = False
        self.current_task = None
        self.task_queue = asyncio.Queue()
        self.setup_logging()
        self.rate_limiter = RateLimiter(calls_per_minute=50)  # 50 calls per minute
        self.token_budget = {
            "small": 1000,  # For simple fixes
            "medium": 2000,  # For moderate code changes
            "large": 4000,  # For complex analysis
        }

    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir / "autonomous_agent.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    async def initialize(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Client(api_key=self.api_key)
        logger.info("Claude agent initialized successfully")

    async def start(self):
        if not self.client:
            logger.error("Agent not initialized. Call initialize() first.")
            return

        self.is_running = True
        logger.info("Starting autonomous agent...")
        await asyncio.gather(self.process_tasks(), self.monitor_system())

    async def stop(self):
        self.is_running = False
        logger.info("Stopping autonomous agent...")

    async def process_tasks(self):
        while self.is_running:
            try:
                # Get pending tasks from task manager
                pending_tasks = await task_manager.get_pending_tasks()
                for task in pending_tasks:
                    await self.task_queue.put(task)
                    await task_manager.update_task_status(task, "in_progress")

                if not self.task_queue.empty():
                    task = await self.task_queue.get()
                    self.current_task = task
                    await self.execute_task(task)
                    await task_manager.update_task_status(task, "completed")
                    self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
            await asyncio.sleep(1)

    async def execute_task(self, task: Dict[str, Any]):
        logger.info(f"Executing task: {task['type']}")
        try:
            if task["type"] == "error_fix":
                await self.handle_error_fix(task)
            else:
                response = await self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    temperature=0.7,
                    system=self.get_system_prompt(),
                    messages=[
                        {"role": "user", "content": self.format_task_prompt(task)}
                    ],
                )
                await self.handle_response(response, task)
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            await task_manager.update_task_status(task, "failed")
            # Create a new task to fix this error
            await task_manager.create_error_fix_task(
                error=str(e),
                file=task.get("file", "unknown"),
                line=0,
                context=f"Error occurred while executing task: {task}",
            )

    async def handle_error_fix(self, task: Dict[str, Any]):
        """Handle error fix tasks with specific error patterns."""
        error = task["error"]
        file = task["file"]

        if "ImportError" in error:
            # Handle missing import
            module = error.split(": ")[1].split(" ")[0]
            await self.fix_import_error(module, file)

        elif "AsyncError" in error:
            # Handle async/await errors
            await self.fix_async_error(file, error)

        elif "AttributeError" in error:
            # Handle missing attributes
            await self.fix_attribute_error(file, error)

        else:
            # Generic error handling
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0.7,
                system=self.get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": f"Fix the following error in {file}:\n{error}\nContext: {task['context']}",
                    }
                ],
            )
            await self.handle_response(response, task)

    async def fix_import_error(self, module: str, file: str):
        """Fix missing import errors."""
        try:
            with open(file, "r") as f:
                content = f.read()

            # Add import statement at the top of the file
            import_stmt = f"from {'.'.join(module.split('.')[:-1])} import {module.split('.')[-1]}\n"
            content = import_stmt + content

            with open(file, "w") as f:
                f.write(content)

            logger.info(f"Added import {module} to {file}")

            # Verify the fix
            await self.verify_fix(file)
        except Exception as e:
            logger.error(f"Failed to fix import error: {e}")

    async def fix_async_error(self, file: str, error: str):
        """Fix async/await related errors."""
        try:
            with open(file, "r") as f:
                content = f.read()

            # Common async/await fixes
            content = content.replace("await message", "message")
            content = content.replace("await response", "response")

            with open(file, "w") as f:
                f.write(content)

            logger.info(f"Fixed async/await error in {file}")

            # Verify the fix
            await self.verify_fix(file)
        except Exception as e:
            logger.error(f"Failed to fix async error: {e}")

    async def fix_attribute_error(self, file: str, error: str):
        """Fix missing attribute errors."""
        try:
            obj_type = error.split("'")[1]
            attribute = error.split("'")[3]

            with open(file, "r") as f:
                content = f.read()

            # Add missing attribute/method
            class_def_pos = content.find(f"class {obj_type}")
            if class_def_pos != -1:
                # Find the end of the class definition
                class_end = content.find("\n\n", class_def_pos)
                if class_end == -1:
                    class_end = len(content)

                # Add the missing attribute/method
                new_attr = f"\n    def {attribute}(self):\n        pass\n"
                content = content[:class_end] + new_attr + content[class_end:]

                with open(file, "w") as f:
                    f.write(content)

                logger.info(
                    f"Added missing attribute {attribute} to {obj_type} in {file}"
                )

                # Verify the fix
                await self.verify_fix(file)
        except Exception as e:
            logger.error(f"Failed to fix attribute error: {e}")

    def get_system_prompt(self) -> str:
        return """You are an autonomous error management agent responsible for detecting and fixing code issues.
                 Follow these directives:
                 1. Analyze code for potential errors and issues
                 2. Propose fixes that maintain code quality and follow best practices
                 3. Document all changes and reasoning
                 4. Consider performance implications
                 5. Ensure backward compatibility
                 6. Follow project's style guidelines"""

    def format_task_prompt(self, task: Dict[str, Any]) -> str:
        if task["type"] == "error_fix":
            with open(task["file"], "r") as f:
                file_content = f.read()
            return f"""Analyze and fix the following error:
                      Error: {task['error']}
                      File: {task['file']}
                      Line: {task['line']}
                      Context: {task['context']}
                      
                      File content:
                      {file_content}
                      
                      Provide the complete fixed code and explain the changes."""
        elif task["type"] == "test_execution":
            return f"""Execute and analyze test file:
                      Test file: {task['test_file']}
                      Analyze test results and propose improvements.
                      
                      Current test output:
                      {self.run_test(task['test_file'])}"""
        elif task["type"] == "linting":
            with open(task["file"], "r") as f:
                file_content = f.read()
            return f"""Perform linting check on file:
                      File: {task['file']}
                      Content: {file_content}
                      Fix any style issues and ensure code follows best practices."""
        return f"Process task of type {task['type']} with data: {task}"

    def run_test(self, test_file: str) -> str:
        """Run a specific test file or test case."""
        try:
            # If test_file contains a specific test case (::), run just that test
            if "::" in test_file:
                file_path, test_case = test_file.split("::", 1)
                if not Path(file_path).exists():
                    return f"Test file not found: {file_path}"
                result = subprocess.run(
                    ["python", "-m", "pytest", f"{file_path}::{test_case}", "-v"],
                    capture_output=True,
                    text=True,
                )
            else:
                # Run the entire test file
                if not Path(test_file).exists():
                    return f"Test file not found: {test_file}"
                result = subprocess.run(
                    ["python", "-m", "pytest", test_file, "-v"],
                    capture_output=True,
                    text=True,
                )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error running test: {str(e)}"

    async def handle_response(self, response: Any, task: Dict[str, Any]):
        """Handle Claude API response."""
        logger.info(f"Handling response for task: {task['type']}")
        try:
            # Extract content from the response object
            response_content = (
                response.content[0].text
                if hasattr(response, "content")
                else str(response)
            )

            if task["type"] == "error_fix":
                # Extract fixed code from response
                fixed_code = self.extract_code_from_response(response_content)
                if fixed_code:
                    with open(task["file"], "w") as f:
                        f.write(fixed_code)
                    logger.info(f"Applied fix to {task['file']}")

                    # Run tests to verify fix
                    await self.verify_fix(task["file"])

            elif task["type"] == "test_execution":
                # Extract test improvements
                improvements = self.extract_test_improvements(response_content)
                if improvements:
                    with open(task["test_file"], "w") as f:
                        f.write(improvements)
                    logger.info(f"Updated test file {task['test_file']}")

            elif task["type"] == "linting":
                # Extract linting fixes
                fixed_code = self.extract_code_from_response(response_content)
                if fixed_code:
                    with open(task["file"], "w") as f:
                        f.write(fixed_code)
                    logger.info(f"Applied linting fixes to {task['file']}")

            await task_manager.update_task_status(task, "completed")

        except Exception as e:
            logger.error(f"Error handling response: {str(e)}")
            await task_manager.update_task_status(task, "failed")

    def extract_code_from_response(self, response: str) -> str:
        """Extract code blocks from Claude's response."""
        import re

        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
        return code_blocks[0] if code_blocks else None

    def extract_test_improvements(self, response: str) -> str:
        """Extract improved test code from response."""
        return self.extract_code_from_response(response)

    async def verify_fix(self, file_path: str):
        """Verify a fix by running related tests."""
        try:
            # Find and run related tests
            test_file = f"tests/test_{Path(file_path).stem}.py"
            if Path(test_file).exists():
                result = subprocess.run(
                    ["python", "-m", "pytest", test_file, "-v"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    logger.warning(f"Fix verification failed for {file_path}")
                    # Create new task to fix test failures
                    await task_manager.create_error_fix_task(
                        error=result.stderr,
                        file=file_path,
                        line=0,
                        context=result.stdout,
                    )
                else:
                    logger.info(f"Fix verified successfully for {file_path}")
        except Exception as e:
            logger.error(f"Error verifying fix: {str(e)}")

    async def monitor_system(self):
        """Monitor system for errors and test failures."""
        while self.is_running:
            try:
                # Run all tests to check for failures
                result = subprocess.run(
                    ["python", "-m", "pytest", "tests/", "-v"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    # Parse test failures and create tasks
                    for line in result.stdout.split("\n"):
                        if "FAILED" in line or "ERROR" in line:
                            # Extract file path and test name
                            parts = line.split(" ")[0].split("::")
                            file_path = parts[0]
                            if not Path(file_path).exists():
                                continue

                            await task_manager.create_error_fix_task(
                                error=line,
                                file=file_path,
                                line=0,
                                context=result.stdout,
                            )

                # Run linting checks
                for py_file in Path("src").rglob("*.py"):
                    result = subprocess.run(
                        ["python", "-m", "flake8", str(py_file)],
                        capture_output=True,
                        text=True,
                    )
                    if result.stdout:
                        await task_manager.create_linting_task(str(py_file))

                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error in system monitoring: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error

    async def add_task(self, task: Dict[str, Any]):
        await self.task_queue.put(task)
        logger.info(f"Added task to queue: {task['type']}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "queue_size": self.task_queue.qsize(),
            "last_update": datetime.now().isoformat(),
        }

    async def fix_error(self, error: str, file: str, line: int, context: str) -> str:
        """Use Claude to fix an error."""
        try:
            prompt = f"""Fix the following error in {file} at line {line}:
            
Error: {error}

Context:
{context}

Please provide the fix and explanation."""

            response = await self.make_api_call(
                prompt=prompt, max_tokens=self.token_budget["medium"]
            )

            if not response:
                return f"Failed to get a valid response from Claude for error: {error}"

            return response
        except Exception as e:
            logger.error(f"Error getting fix from Claude: {str(e)}")
            return f"Failed to get fix from Claude: {str(e)}"

    async def fix_linting(self, file: str) -> str:
        """Use Claude to fix linting issues."""
        try:
            with open(file, "r") as f:
                code = f.read()

            # Calculate token budget based on code size
            code_size = len(code)
            if code_size < 1000:
                budget = self.token_budget["small"]
            elif code_size < 5000:
                budget = self.token_budget["medium"]
            else:
                budget = self.token_budget["large"]

            prompt = f"""Fix the following Python code to comply with PEP8 and common linting rules:

{code}

Please provide the fixed code with explanations of the changes."""

            response = await self.make_api_call(prompt=prompt, max_tokens=budget)

            if not response:
                return f"Failed to get a valid response from Claude for linting {file}"

            return response
        except Exception as e:
            logger.error(f"Error getting linting fix from Claude: {str(e)}")
            return f"Failed to get linting fix from Claude: {str(e)}"

    async def make_api_call(
        self, prompt: str, max_tokens: int, temperature: float = 0
    ) -> Optional[str]:
        """Make a rate-limited API call to Claude."""
        await self.rate_limiter.acquire()

        try:
            message = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text if message.content else None
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return None


autonomous_agent = ClaudeAutonomousAgent()
