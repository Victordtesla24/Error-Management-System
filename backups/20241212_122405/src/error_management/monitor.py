"""File monitoring and automatic error fixing."""

import logging
import logging.config  # Add explicit import for logging.config
import subprocess
import sys
import time
from pathlib import Path
from typing import Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/monitor.log"),
    ],
)
logger = logging.getLogger(__name__)


class ErrorFixingHandler(FileSystemEventHandler):
    """Handle file system events and trigger error detection/fixing."""

    def __init__(self, project_path: Path):
        """Initialize handler."""
        self.project_path = project_path
        self.last_run = 0
        self.debounce_seconds = 2
        self.ignore_patterns: Set[str] = {
            "*.pyc",
            "__pycache__",
            "*.log",
            "*.bak",
            ".git",
            ".pytest_cache",
            "*.egg-info",
        }

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if file should be ignored
        file_path = Path(event.src_path)
        if any(pattern in str(file_path) for pattern in self.ignore_patterns):
            return

        # Debounce to avoid multiple runs
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
        self.last_run = current_time

        try:
            # Run tests to detect errors
            logger.info(f"Running tests for changes in {file_path}")
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            # Process test output
            if result.returncode != 0:
                logger.info("Tests failed - triggering error fixes")
                # Run verify and fix script
                fix_result = subprocess.run(
                    ["./scripts/verify_and_fix.sh"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                )
                if fix_result.returncode == 0:
                    logger.info("Fixes applied successfully")
                else:
                    logger.error(f"Fix script failed: {fix_result.stderr}")
            else:
                logger.info("All tests passed")

        except Exception as e:
            logger.error(f"Error running tests/fixes: {str(e)}")


def start_monitoring(project_path: Path = None):
    """Start file monitoring."""
    if project_path is None:
        project_path = Path.cwd()

    logger.info(f"Starting file monitoring for {project_path}")

    # Create observer and handler
    observer = Observer()
    handler = ErrorFixingHandler(project_path)

    # Add watchers for key directories
    paths_to_watch = [
        project_path / "src",
        project_path / "tests",
        project_path / "scripts",
    ]

    for path in paths_to_watch:
        if path.exists():
            observer.schedule(handler, str(path), recursive=True)
            logger.info(f"Monitoring {path}")

    # Start observer
    observer.start()
    logger.info("File monitoring started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File monitoring stopped")

    observer.join()


if __name__ == "__main__":
    start_monitoring()
