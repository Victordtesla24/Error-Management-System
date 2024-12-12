"""Continuous error monitoring and fixing system."""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Set

import pytest
from watchdog.events import FileSystemEventHandler

from src.error_management.simple_handler import error_handler
from src.error_management.test_fixer import test_fixer

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


class ContinuousErrorMonitor(FileSystemEventHandler):
    """Monitor and fix errors continuously."""

    def __init__(self, project_path: Path):
        """Initialize monitor."""
        self.project_path = project_path
        self.last_check = 0
        self.check_interval = 5  # seconds
        self.ignore_patterns: Set[str] = {
            "*.pyc",
            "__pycache__",
            "*.log",
            "*.bak",
            ".git",
            ".pytest_cache",
            "*.egg-info",
        }
        self.running = False

    async def start(self):
        """Start continuous monitoring."""
        self.running = True
        logger.info("Starting continuous error monitoring")

        while self.running:
            try:
                await self._check_for_errors()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

    async def _check_for_errors(self):
        """Check for and fix errors."""
        try:
            current_time = time.time()
            if current_time - self.last_check < self.check_interval:
                return
            self.last_check = current_time

            # Run tests to detect errors
            logger.info("Running tests to check for errors...")
            result = pytest.main(["-v", "--tb=short", "tests/"])

            if result != 0:
                logger.info("Errors detected, applying fixes...")

                # Get fix report
                report = test_fixer.get_fix_report()
                if report["total_fixes"] > 0:
                    logger.info("\nFixes applied:")
                    for test in report["fixed_tests"]:
                        logger.info(f"\n{test['name']}:")
                        for fix in test["fixes"]:
                            logger.info(f"  - {fix['description']}")

                    # Verify fixes
                    logger.info("\nVerifying fixes...")
                    verify_result = pytest.main(["-v", "--tb=short", "tests/"])
                    if verify_result == 0:
                        logger.info("All errors fixed successfully")
                    else:
                        logger.warning("Some errors remain after fixes")
            else:
                logger.info("No errors detected")

            # Log statistics
            stats = error_handler.get_stats()
            logger.info("\nError Management Statistics:")
            logger.info(f"Total errors encountered: {stats['total_errors']}")
            logger.info(f"Unique error types: {stats['unique_errors']}")
            if stats["error_counts"]:
                logger.info("Error counts by type:")
                for error_type, count in stats["error_counts"].items():
                    logger.info(f"  {error_type}: {count}")

        except Exception as e:
            logger.error(f"Error checking for errors: {str(e)}")

    def stop(self):
        """Stop continuous monitoring."""
        self.running = False
        logger.info("Stopping continuous error monitoring")


async def main():
    """Run continuous monitoring."""
    project_path = Path.cwd()
    monitor = ContinuousErrorMonitor(project_path)

    try:
        await monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
