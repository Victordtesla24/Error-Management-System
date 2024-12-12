"""Autonomous error fixing system."""

import logging
import sys
import time
from pathlib import Path
from typing import Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.error_management.test_fixer import test_fixer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/autonomous_fixer.log"),
    ],
)
logger = logging.getLogger(__name__)


class ErrorFixingHandler(FileSystemEventHandler):
    """Handle file system events and trigger error fixing."""

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
            logger.info(f"Change detected in {file_path}")

            # Run tests if Python file changed
            if file_path.suffix == ".py":
                self._handle_python_file_change(file_path)

        except Exception as e:
            logger.error(f"Error handling file change: {str(e)}")

    def _handle_python_file_change(self, file_path: Path):
        """Handle changes to Python files."""
        try:
            import pytest

            logger.info("Running tests...")

            # Run pytest with our error fixing plugin
            result = pytest.main(
                [
                    "-v",
                    "--tb=short",
                    str(file_path) if file_path.is_file() else "tests/",
                ]
            )

            # Get fix report
            report = test_fixer.get_fix_report()

            if report["total_fixes"] > 0:
                logger.info("\nFixes applied:")
                for test in report["fixed_tests"]:
                    logger.info(f"\n{test['name']}:")
                    for fix in test["fixes"]:
                        logger.info(f"  - {fix['description']}")

            # Run tests again to verify fixes
            if report["total_fixes"] > 0:
                logger.info("\nRe-running tests to verify fixes...")
                verify_result = pytest.main(
                    [
                        "-v",
                        "--tb=short",
                        str(file_path) if file_path.is_file() else "tests/",
                    ]
                )

                if verify_result == 0:
                    logger.info("All tests passing after fixes")
                else:
                    logger.warning("Some tests still failing after fixes")

        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")


def start_autonomous_fixing(project_path: Path = None):
    """Start autonomous error fixing."""
    if project_path is None:
        project_path = Path.cwd()

    logger.info(f"Starting autonomous error fixing for {project_path}")

    # Create observer and handler
    observer = Observer()
    handler = ErrorFixingHandler(project_path)

    # Add watchers for key directories
    paths_to_watch = [project_path / "src", project_path / "tests"]

    for path in paths_to_watch:
        if path.exists():
            observer.schedule(handler, str(path), recursive=True)
            logger.info(f"Monitoring {path}")

    # Start observer
    observer.start()
    logger.info("Autonomous error fixing started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Autonomous error fixing stopped")

    observer.join()


if __name__ == "__main__":
    start_autonomous_fixing()
