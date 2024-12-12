"""Pytest plugin for error management integration."""

import logging
from typing import Any, Dict, Optional

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport

from .error_handler import error_handler
from .service import error_management_service

logger = logging.getLogger(__name__)


def pytest_configure(config: Config) -> None:
    """Configure pytest plugin."""
    try:
        # Initialize error management service
        error_management_service.start()
        logger.info("Error management service initialized for testing")
    except Exception as e:
        logger.error(f"Failed to initialize error management: {str(e)}")


def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> bool:
    """Handle test execution and error capture."""
    try:
        # Add test context to error handler
        error_handler.current_test = {
            "name": item.name,
            "path": str(item.path),
            "function": item.function.__name__,
        }
        return False  # Let pytest handle the test
    except Exception as e:
        logger.error(f"Error in test protocol: {str(e)}")
        return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: Any) -> Any:
    """Process test results and capture errors."""
    outcome = yield
    report = outcome.get_result()

    try:
        if report.when == "call":
            if report.failed:
                # Extract error information
                error_info = _extract_error_info(report)
                if error_info:
                    # Create error fix task
                    task = {
                        "type": error_info["type"],
                        "message": error_info["message"],
                        "file_path": str(item.path),
                        "line_number": error_info.get("line_number", 0),
                        "context": {
                            "test": item.name,
                            "phase": "test",
                            "traceback": error_info.get("traceback"),
                        },
                    }

                    # Log error and create fix task
                    logger.error(
                        f"Test failure in {item.name}: {error_info['message']}"
                    )
                    error_handler.handle_error_task(task)
    except Exception as e:
        logger.error(f"Error processing test report: {str(e)}")


def _extract_error_info(report: TestReport) -> Optional[Dict[str, Any]]:
    """Extract error information from test report."""
    try:
        if report.longrepr:
            if hasattr(report.longrepr, "reprcrash"):
                crash = report.longrepr.reprcrash
                return {
                    "type": crash.message.split(":")[0],
                    "message": crash.message,
                    "line_number": crash.lineno,
                    "traceback": str(report.longrepr),
                }
            return {
                "type": "TestError",
                "message": str(report.longrepr),
                "traceback": str(report.longrepr),
            }
        return None
    except Exception as e:
        logger.error(f"Error extracting error info: {str(e)}")
        return None


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    """Clean up after test session."""
    try:
        # Clear test context
        error_handler.current_test = None

        # Log test session results
        logger.info(f"Test session finished with status {exitstatus}")

        # Get error statistics
        stats = error_handler.get_error_stats()
        logger.info(f"Error statistics: {stats}")
    except Exception as e:
        logger.error(f"Error in session finish: {str(e)}")


@pytest.fixture(autouse=True)
def error_management_fixture():
    """Fixture to ensure error management is active for all tests."""
    try:
        # Setup
        error_handler.start_test_mode()
        yield
        # Teardown
        error_handler.end_test_mode()
    except Exception as e:
        logger.error(f"Error in fixture: {str(e)}")
        raise
