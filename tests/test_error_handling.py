"""Test script to demonstrate automatic error handling."""

import logging
import sys
from pathlib import Path

from src.error_management.simple_handler import error_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/test_errors.log"),
    ],
)
logger = logging.getLogger(__name__)


# Test functions with automatic error handling
@error_handler.handle
def test_import_error():
    """Test handling of import errors."""
    import nonexistent_module

    return nonexistent_module


@error_handler.handle
def test_type_error():
    """Test handling of type errors."""
    from src.error_management.error import Error

    # This will trigger type error that our handler knows how to fix
    error = Error(type="test")
    return error


@error_handler.handle
def test_syntax_error():
    """Test handling of syntax errors."""
    # Create a file with syntax error
    test_file = Path("test_syntax.py")
    test_file.write_text(
        "def broken_function():\n    print('Hello'\n"
    )  # Missing parenthesis

    # Try to import it
    import test_syntax

    return test_syntax


def main():
    """Run error handling tests."""
    logger.info("Starting error handling tests")

    try:
        # Test import error handling
        logger.info("\nTesting import error handling...")
        test_import_error()
    except Exception as e:
        logger.error(f"Import error test failed: {str(e)}")

    try:
        # Test type error handling
        logger.info("\nTesting type error handling...")
        test_type_error()
    except Exception as e:
        logger.error(f"Type error test failed: {str(e)}")

    try:
        # Test syntax error handling
        logger.info("\nTesting syntax error handling...")
        test_syntax_error()
    except Exception as e:
        logger.error(f"Syntax error test failed: {str(e)}")

    # Print error statistics
    stats = error_handler.get_stats()
    logger.info("\nError handling statistics:")
    logger.info(f"Total errors: {stats['total_errors']}")
    logger.info(f"Unique error types: {stats['unique_errors']}")
    logger.info(f"Error counts by type: {stats['error_counts']}")


if __name__ == "__main__":
    main()
