"""Test configuration and fixtures."""

import logging
import os
import sys
from pathlib import Path

import pytest

from src.error_management.simple_handler import error_handler
from src.error_management.test_fixer import test_fixer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("logs/test.log")],
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return Path(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def error_management(project_root):
    """Initialize error management system for tests."""
    logger.info("Initializing error management system for tests")

    # Configure error handler
    error_handler.project_path = project_root

    # Configure test fixer
    test_fixer.fixes_applied.clear()

    yield {"error_handler": error_handler, "test_fixer": test_fixer}

    # Print error statistics at end of session
    stats = error_handler.get_stats()
    logger.info("\nError Management Statistics:")
    logger.info(f"Total errors encountered: {stats['total_errors']}")
    logger.info(f"Unique error types: {stats['unique_errors']}")
    logger.info("Error counts by type:")
    for error_type, count in stats["error_counts"].items():
        logger.info(f"  {error_type}: {count}")

    # Print fix report
    report = test_fixer.get_fix_report()
    if report["total_fixes"] > 0:
        logger.info("\nFixes Applied:")
        for test in report["fixed_tests"]:
            logger.info(f"\n{test['name']}:")
            for fix in test["fixes"]:
                logger.info(f"  - {fix['description']}")


@pytest.fixture(autouse=True)
def auto_error_management(error_management):
    """Automatically enable error management for all tests."""
    yield error_management


@pytest.fixture
def test_data_dir(project_root):
    """Get test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir
