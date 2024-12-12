"""
File Monitor - Monitors file system changes and triggers error detection
"""

import ast
import asyncio
import fnmatch
import hashlib
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import aiofiles
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.error_management.error_context import ErrorContext
from src.error_management.error_manager import ErrorManager
from src.error_management.models import Error
from src.error_management.secure_environment import SecureEnvironment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define dangerous patterns
DANGEROUS_PATTERNS = [
    (r"os\.system\s*\(", "System command execution detected"),
    (r"subprocess\.(Popen|call|run)", "Subprocess execution detected"),
    (r"eval\s*\(", "Eval usage detected"),
    (r"exec\s*\(", "Exec usage detected"),
    (r"__import__\s*\(", "Dynamic import detected"),
    (r'open\s*\(.+,\s*[\'"]w[\'"]\)', "File write operation detected"),
    (r"(rm|remove|rmdir|unlink)\s*\(", "File deletion operation detected"),
]


class FileMonitor(FileSystemEventHandler):
    """Monitor files for changes and errors."""

    def __init__(self, project_root: Path, error_manager):
        """Initialize FileMonitor.

        Args:
            project_root: Path to project root directory
            error_manager: Error manager instance
        """
        self.project_root = Path(project_root).resolve()
        self.error_manager = error_manager
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.observer = Observer()
        self.loop = None
        self.excluded_patterns = {
            "*.pyc",
            "__pycache__",
            ".git",
            "node_modules",
            "*.tmp",
            ".pytest_cache",
        }

    def should_monitor_file(self, file_path: Path) -> bool:
        """Check if a file should be monitored."""
        try:
            file_path = Path(file_path).resolve()

            # Check if file is within project
            if not str(file_path).startswith(str(self.project_root)):
                return False

            # Check excluded patterns
            path_str = str(file_path)
            for pattern in self.excluded_patterns:
                if pattern.startswith("*."):
                    if path_str.endswith(pattern[1:]):
                        return False
                elif pattern in path_str:
                    return False

            # Only monitor Python files
            return file_path.suffix == ".py"

        except Exception as e:
            logging.error(f"Error checking file: {e}")
            return False

    def _check_unreachable_code(self, node: ast.FunctionDef) -> Optional[int]:
        """Check for unreachable code in a function.

        Returns the line number of the return statement if unreachable code is found,
        otherwise returns None.
        """
        has_return = False
        return_line = None

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return):
                has_return = True
                return_line = stmt.lineno
            elif has_return and hasattr(stmt, "lineno") and stmt.lineno > return_line:
                return return_line

        return None

    async def analyze_python_file(self, file_path: Path) -> None:
        """Analyze a Python file for errors."""
        try:
            if not self.should_monitor_file(file_path):
                return

            with open(file_path, "r") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                error = Error(
                    id=f"{file_path}:{e.lineno}",
                    file_path=file_path,
                    line_number=e.lineno,
                    error_type="SyntaxError",
                    message=str(e),
                )
                await self.error_manager.add_error_async(error)
                return

            # Check for common issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for missing docstring
                    if not ast.get_docstring(node):
                        error = Error(
                            id=f"{file_path}:{node.lineno}",
                            file_path=file_path,
                            line_number=node.lineno,
                            error_type="Style",
                            message=f"Missing docstring in function '{node.name}'",
                        )
                        await self.error_manager.add_error_async(error)

                    # Check for unreachable code
                    if return_line := self._check_unreachable_code(node):
                        error = Error(
                            id=f"{file_path}:{return_line}",
                            file_path=file_path,
                            line_number=return_line,
                            error_type="Logic",
                            message="Unreachable code after return statement",
                        )
                        await self.error_manager.add_error_async(error)

        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {e}")

    async def start(self):
        """Start monitoring files."""
        if self.running:
            return

        self.running = True
        self.loop = asyncio.get_event_loop()
        self.observer.schedule(self, str(self.project_root), recursive=True)
        self.observer.start()
        self.task = self.loop.create_task(self._monitor())

        # Initial analysis of existing files
        for file_path in self.project_root.rglob("*.py"):
            await self.analyze_python_file(file_path)

    async def stop(self):
        """Stop monitoring files."""
        if not self.running:
            return

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        self.observer.stop()
        self.observer.join()

    async def _monitor(self):
        """Monitor files for changes."""
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Error in file monitor: {e}")

    def on_modified(self, event):
        """Handle file modification events."""
        if not isinstance(event, FileModifiedEvent):
            return

        file_path = Path(event.src_path)
        if self.should_monitor_file(file_path):
            if self.loop is None:
                try:
                    self.loop = asyncio.get_event_loop()
                except RuntimeError:
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)

            asyncio.run_coroutine_threadsafe(
                self.analyze_python_file(file_path), self.loop
            )

    async def analyze_file(self, filepath: str):
        """Analyze a file for errors."""
        try:
            async with aiofiles.open(filepath, "r") as f:
                content = await f.read()

                # Check for bare except
                if "except:" in content:
                    error = Error(
                        id=f"{filepath}:1",
                        file_path=filepath,
                        line_number=1,
                        error_type="BareExcept",
                        message="Bare except found",
                        timestamp=datetime.now(),
                    )
                    await self.error_manager.add_error(error)

                # Check for dangerous patterns
                for pattern, message in DANGEROUS_PATTERNS:
                    if re.search(pattern, content):
                        error = Error(
                            id=f"{filepath}:{content.count(chr(10)) + 1}",
                            file_path=filepath,
                            line_number=content.count(chr(10)) + 1,
                            error_type="SecurityIssue",
                            message=message,
                            timestamp=datetime.now(),
                        )
                        await self.error_manager.add_error(error)

        except Exception as e:
            logger.error(f"Error analyzing file {filepath}: {e}")

    async def scan_files(self):
        """Scan files in the project directory."""
        try:
            for root, _, files in os.walk(self.project_root):
                for file in files:
                    filepath = os.path.join(root, file)
                    if self.should_monitor_file(Path(filepath)):
                        await self.analyze_file(filepath)
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
            raise


class FileObserver:
    """File observer for monitoring file changes."""

    def __init__(self, monitor):
        """Initialize file observer."""
        self._monitor = monitor
        self._running = False
        self._task = None
        self._loop = None

    async def start(self):
        """Start observing files."""
        if not self._running:
            self._running = True
            self._loop = asyncio.get_event_loop()
            self._task = self._loop.create_task(self._observe())

    async def stop(self):
        """Stop observing files."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def is_alive(self) -> bool:
        """Check if observer is running."""
        return self._running and (self._task is not None and not self._task.done())

    async def _observe(self):
        """Observe files for changes."""
        try:
            while self._running:
                await self._monitor.scan_files()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._monitor.logger.error(f"Error in file observer: {e}")
            raise
