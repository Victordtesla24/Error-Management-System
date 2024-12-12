"""Log monitoring module for autonomous error detection."""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .error_manager import ErrorManager
from .task_manager import task_manager

logger = logging.getLogger(__name__)


class LogMonitor:
    """Monitors logs for errors and triggers automatic fixes."""

    def __init__(self):
        self.setup_logging()
        self.log_dir = Path("logs")
        self.error_patterns = {
            r"Failed to load (\w+): name '(\w+)' is not defined": self._handle_import_error,
            r"Error executing task: (.+)": self._handle_task_error,
            r"object (\w+) can't be used in 'await' expression": self._handle_await_error,
            r"AttributeError: '(\w+)' object has no attribute '(\w+)'": self._handle_attribute_error,
        }
        self.known_errors: Set[str] = set()
        self.running = False
        self.error_manager = ErrorManager()

    def setup_logging(self):
        """Set up logging for log monitor."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        fh = logging.FileHandler(log_dir / "log_monitor.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)

        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)

    async def start(self):
        """Start monitoring logs."""
        self.running = True
        logger.info("Starting log monitor")
        await asyncio.gather(self.monitor_logs(), self.cleanup_stale_tasks())

    async def stop(self):
        """Stop monitoring logs."""
        self.running = False
        logger.info("Stopping log monitor")

    async def monitor_logs(self):
        """Monitor log files for errors."""
        while self.running:
            try:
                for log_file in self.log_dir.glob("*.log"):
                    await self.scan_log_file(log_file)
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error monitoring logs: {e}")
                await asyncio.sleep(5)

    async def scan_log_file(self, log_file: Path):
        """Scan a log file for errors."""
        try:
            with open(log_file, "r") as f:
                lines = f.readlines()

            for line in lines[-1000:]:  # Check last 1000 lines
                for pattern, handler in self.error_patterns.items():
                    if match := re.search(pattern, line):
                        error_key = f"{log_file.name}:{match.group()}"
                        if error_key not in self.known_errors:
                            self.known_errors.add(error_key)
                            await handler(match, line)
        except Exception as e:
            logger.error(f"Error scanning log file {log_file}: {e}")

    async def cleanup_stale_tasks(self):
        """Clean up stale tasks periodically."""
        while self.running:
            try:
                await task_manager.cleanup_stale_tasks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error cleaning up stale tasks: {e}")
                await asyncio.sleep(60)

    async def _handle_import_error(self, match: re.Match, line: str):
        """Handle import-related errors."""
        module = match.group(2)
        logger.info(f"Detected missing import for {module}")

        # Create fix task
        await task_manager.create_error_fix_task(
            error=f"ImportError: {module} not found",
            file=line.split(" - ")[1].split(":")[0],
            line=0,
            context=line,
        )

    async def _handle_task_error(self, match: re.Match, line: str):
        """Handle task execution errors."""
        error_msg = match.group(1)
        logger.info(f"Detected task error: {error_msg}")

        # Create fix task
        await task_manager.create_error_fix_task(
            error=error_msg,
            file=line.split(" - ")[1].split(":")[0],
            line=0,
            context=line,
        )

    async def _handle_await_error(self, match: re.Match, line: str):
        """Handle async/await errors."""
        obj_type = match.group(1)
        logger.info(f"Detected await error for {obj_type}")

        # Create fix task
        await task_manager.create_error_fix_task(
            error=f"AsyncError: {obj_type} cannot be awaited",
            file=line.split(" - ")[1].split(":")[0],
            line=0,
            context=line,
        )

    async def _handle_attribute_error(self, match: re.Match, line: str):
        """Handle attribute errors."""
        obj_type = match.group(1)
        attribute = match.group(2)
        logger.info(f"Detected missing attribute {attribute} for {obj_type}")

        # Create fix task
        await task_manager.create_error_fix_task(
            error=f"AttributeError: {obj_type} has no attribute {attribute}",
            file=line.split(" - ")[1].split(":")[0],
            line=0,
            context=line,
        )


log_monitor = LogMonitor()
