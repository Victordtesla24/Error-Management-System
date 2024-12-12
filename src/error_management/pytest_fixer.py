"""Pytest plugin for automatic test fixing."""

import logging
import sys
from typing import Any, Optional

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport

from .test_fixer import test_fixer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/pytest_fixer.log"),
    ],
)
logger = logging.getLogger(__name__)


def pytest_configure(config: Config) -> None:
    """Configure pytest plugin."""
    logger.info("Initializing test fixer plugin")


def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> bool:
    """Handle test execution with automatic fixing."""
    test_fixer.start_test(item.name, str(item.path))
    return False  # Let pytest handle the test


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: Any) -> Any:
    """Process test results and fix failures."""
    outcome = yield
    report = outcome.get_result()

    try:
        if report.when == "call" and report.failed:
            logger.info(f"Test failed: {item.name}")

            # Extract error information
            if hasattr(report, "longrepr"):
                error_msg = str(report.longrepr)
                error_type = error_msg.split(":")[0] if ":" in error_msg else "Unknown"

                # Create error from message
                error = Exception(error_msg)
                error.__class__.__name__ = error_type

                # Attempt to fix the error
                if test_fixer.fix_test_error(error, str(item.path), item.name):
                    logger.info(f"Fixed error in test: {item.name}")
                    # Rerun the test
                    item.ihook.pytest_runtest_call(item=item)
    except Exception as e:
        logger.error(f"Error in test fixing: {str(e)}")


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    """Generate fix report at end of test session."""
    try:
        test_fixer.end_test()
        report = test_fixer.get_fix_report()

        logger.info("\nTest Fix Report:")
        logger.info(f"Total tests processed: {report['total_tests']}")
        logger.info(f"Total fixes applied: {report['total_fixes']}")
        logger.info("\nFixes by error type:")
        for error_type, count in report["fixes_by_type"].items():
            logger.info(f"  {error_type}: {count}")

        logger.info("\nFixed tests:")
        for test in report["fixed_tests"]:
            logger.info(f"\n{test['name']} ({test['file']}):")
            for fix in test["fixes"]:
                logger.info(f"  - {fix['description']}")
    except Exception as e:
        logger.error(f"Error generating fix report: {str(e)}")


@pytest.fixture(autouse=True)
def auto_fix_fixture():
    """Fixture to ensure test fixing is active for all tests."""
    yield  # Let test run
    test_fixer.end_test()  # Clean up after test
