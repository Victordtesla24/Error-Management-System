"""Agent manager module for managing autonomous agents."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .error_manager import ErrorManager
from .file_analyzer import FileAnalyzer


class AgentManager:
    """Manages autonomous agents and their tasks."""

    def __init__(self, base_path: str = "."):
        """Initialize the agent manager.

        Args:
            base_path: Base path for agent operations
        """
        self.base_path = Path(base_path)
        self.setup_logging()
        self.error_manager = ErrorManager(str(self.base_path))
        self.file_analyzer = FileAnalyzer(str(self.base_path))
        self.tasks: List[Dict] = []
        self._stop_event = asyncio.Event()

    def setup_logging(self):
        """Set up logging for agent manager."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure file handler
        fh = logging.FileHandler(log_dir / "agent_manager.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)

        # Get logger
        self.logger = logging.getLogger("agent_manager")

        # Add handler if not already added
        if not any(isinstance(h, logging.FileHandler) for h in self.logger.handlers):
            self.logger.addHandler(fh)
            self.logger.setLevel(logging.INFO)

    async def start(self):
        """Start the agent manager."""
        try:
            self.logger.info("Starting agent manager")
            await self._monitor_files()
        except Exception as e:
            self.logger.error(f"Failed to start agent manager: {str(e)}")
            raise

    async def stop(self):
        """Stop the agent manager."""
        try:
            self.logger.info("Stopping agent manager")
            self._stop_event.set()
        except Exception as e:
            self.logger.error(f"Failed to stop agent manager: {str(e)}")
            raise

    async def _monitor_files(self):
        """Monitor files for changes."""
        while not self._stop_event.is_set():
            try:
                # Analyze files
                results = self.file_analyzer.analyze_directory()

                # Check for issues
                for file_path, analysis in results.items():
                    if analysis.get("issues"):
                        self.logger.warning(
                            f"Issues found in {file_path}: {analysis['issues']}"
                        )
                        await self._handle_issues(file_path, analysis["issues"])

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                self.logger.error(f"Error monitoring files: {str(e)}")
                await asyncio.sleep(10)  # Wait longer on error

    async def _handle_issues(self, file_path: str, issues: List[str]):
        """Handle issues found in files.

        Args:
            file_path: Path to the file with issues
            issues: List of issues found
        """
        for issue in issues:
            task = {
                "type": "fix_issue",
                "file_path": file_path,
                "issue": issue,
                "status": "pending",
            }
            self.tasks.append(task)
            self.logger.info(f"Added task for {file_path}: {issue}")

    def get_tasks(self) -> List[Dict]:
        """Get list of all tasks.

        Returns:
            List of task dictionaries
        """
        return self.tasks

    def get_active_tasks(self) -> List[Dict]:
        """Get list of active tasks.

        Returns:
            List of active task dictionaries
        """
        return [t for t in self.tasks if t["status"] == "pending"]

    def get_completed_tasks(self) -> List[Dict]:
        """Get list of completed tasks.

        Returns:
            List of completed task dictionaries
        """
        return [t for t in self.tasks if t["status"] == "completed"]


# Create singleton instance
agent_manager = AgentManager()
