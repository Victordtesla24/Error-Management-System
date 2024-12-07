"""
File Monitor Module for Error Management System
Handles file system monitoring and change detection
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Set

from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .error_manager import ErrorManager
from .secure_environment import SecureEnvironment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureFileHandler(FileSystemEventHandler):
    """
    Secure file event handler
    Validates and processes file system events
    """

    def __init__(self, secure_env: SecureEnvironment, error_manager: ErrorManager):
        """Initialize secure file handler"""
        self.secure_env = secure_env
        self.error_manager = error_manager
        self.loop = asyncio.get_event_loop()

    def on_modified(self, event):
        """Handle file modification events"""
        if not isinstance(event, FileModifiedEvent):
            return

        try:
            file_path = Path(event.src_path)
            if not self.secure_env.validate_operation("read", file_path):
                logger.warning(f"Access denied to modified file: {file_path}")
                return

            asyncio.run_coroutine_threadsafe(
                self._handle_file_change(file_path), self.loop
            )

        except Exception as e:
            logger.error(f"Error handling file modification: {str(e)}")

    def on_created(self, event):
        """Handle file creation events"""
        if not isinstance(event, FileCreatedEvent):
            return

        try:
            file_path = Path(event.src_path)
            if not self.secure_env.validate_operation("read", file_path):
                logger.warning(f"Access denied to created file: {file_path}")
                return

            asyncio.run_coroutine_threadsafe(
                self._handle_file_change(file_path), self.loop
            )

        except Exception as e:
            logger.error(f"Error handling file creation: {str(e)}")

    async def _handle_file_change(self, file_path: Path):
        """
        Handle file changes

        Args:
            file_path: Path to changed file
        """
        try:
            # Only analyze Python files
            if file_path.suffix == ".py":
                await self.error_manager._analyze_python_file(file_path)

        except Exception as e:
            logger.error(f"Error analyzing changed file: {str(e)}")


class FileMonitor:
    """
    File system monitor
    Watches for file changes and triggers analysis
    """

    def __init__(self, secure_env: SecureEnvironment, error_manager: ErrorManager):
        """
        Initialize file monitor

        Args:
            secure_env: Secure environment instance
            error_manager: Error manager instance
        """
        self.secure_env = secure_env
        self.error_manager = error_manager
        self.observer: Optional[Observer] = None
        self.monitored_paths: Set[Path] = set()
        self._running = False
        logger.info("File monitor initialized")

    async def start_monitoring(self):
        """Start file monitoring"""
        if self._running:
            return

        try:
            self.observer = Observer()
            event_handler = SecureFileHandler(self.secure_env, self.error_manager)

            # Monitor project directory
            project_path = self.secure_env.security_context.project_path
            self.observer.schedule(event_handler, str(project_path), recursive=True)
            self.monitored_paths.add(project_path)

            self.observer.start()
            self._running = True
            logger.info("File monitoring started")

        except Exception as e:
            logger.error(f"Error starting file monitor: {str(e)}")
            self.observer = None
            self._running = False

    async def stop_monitoring(self):
        """Stop file monitoring"""
        if self.observer and self.observer.is_alive():
            try:
                self.observer.stop()
                self.observer.join()
                self.monitored_paths.clear()
                self._running = False
                logger.info("File monitoring stopped")
            except Exception as e:
                logger.error(f"Error stopping file monitor: {str(e)}")

    def is_monitoring(self, path: Path) -> bool:
        """
        Check if a path is being monitored

        Args:
            path: Path to check

        Returns:
            bool: True if path is monitored
        """
        return any(path.is_relative_to(monitored) for monitored in self.monitored_paths)


async def main():
    """Main entry point"""
    try:
        secure_env = SecureEnvironment("./test_project")
        error_manager = ErrorManager(secure_env)
        file_monitor = FileMonitor(secure_env, error_manager)

        await file_monitor.start_monitoring()
        await asyncio.sleep(60)  # Monitor for 1 minute
        await file_monitor.stop_monitoring()

    except Exception as e:
        logger.error(f"Error in file monitor: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
