"""Demonstrate complete error management workflow."""

import logging
import sys
import time
from pathlib import Path

from src.error_management.simple_handler import error_handler
from src.error_management.test_fixer import test_fixer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("logs/demo.log")],
)
logger = logging.getLogger(__name__)


def create_test_with_error():
    """Create a test file with a known error."""
    test_file = Path("tests/test_generated.py")
    content = """
import pytest
from src.error_management.error import Error
from src.error_management.simple_handler import error_handler

@error_handler.handle
class TestGenerated:
    def test_type_error(self):
        # This will trigger a type error
        error = Error(type="test")  # Should be error_type
        assert error.error_type == "test"
    
    def test_attribute_error(self):
        error = Error(error_type="test")
        # This will trigger an attribute error
        assert error.nonexistent_attribute == "value"
    
    def test_assertion_error(self):
        value = 42
        # This will trigger an assertion error
        assert value == 0
"""
    test_file.write_text(content)
    logger.info(f"Created test file: {test_file}")
    return test_file


def run_demo():
    """Run error management demonstration."""
    try:
        logger.info("Starting error management demo")

        # Create test file with errors
        test_file = create_test_with_error()

        # Run tests first time - should have errors
        logger.info("\nRunning tests first time (with errors)...")
        import pytest

        pytest.main(["-v", str(test_file)])

        # Wait for error fixing system to process
        logger.info("\nWaiting for error fixing system...")
        time.sleep(2)

        # Get fix report
        report = test_fixer.get_fix_report()
        if report["total_fixes"] > 0:
            logger.info("\nFixes applied:")
            for test in report["fixed_tests"]:
                logger.info(f"\n{test['name']}:")
                for fix in test["fixes"]:
                    logger.info(f"  - {fix['description']}")

        # Run tests again - should be fixed
        logger.info("\nRunning tests again (after fixes)...")
        pytest.main(["-v", str(test_file)])

        # Show error statistics
        stats = error_handler.get_stats()
        logger.info("\nError handling statistics:")
        logger.info(f"Total errors encountered: {stats['total_errors']}")
        logger.info(f"Unique error types: {stats['unique_errors']}")
        logger.info("Error counts by type:")
        for error_type, count in stats["error_counts"].items():
            logger.info(f"  {error_type}: {count}")

        logger.info("\nDemo completed")

    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        raise


if __name__ == "__main__":
    run_demo()
