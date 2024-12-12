"""Run system with runtime error fixing."""

import logging
import sys
from pathlib import Path

from src.error_management.runtime_fixer import runtime_fixer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/runtime.log"),
    ],
)
logger = logging.getLogger(__name__)


@runtime_fixer.auto_fix
def main():
    """Run main process with error fixing."""
    logger.info("Starting system with runtime error fixing")

    try:
        # Import and use ErrorContext (will be auto-fixed)
        from src.error_management.models import ErrorContext

        logger.info("Successfully imported ErrorContext")

        # Create error with wrong parameter (will be auto-fixed)
        from src.error_management.error import Error

        error = Error(type="test_error")  # Should be error_type
        logger.info("Successfully created Error instance")

        # Try to use nonexistent module (will be auto-fixed)
        import colorama  # Will be installed if missing

        logger.info("Successfully imported colorama")

        logger.info("All operations completed successfully")

        # Show error statistics
        stats = runtime_fixer.get_stats()
        logger.info("\nError Management Statistics:")
        logger.info(f"Total errors encountered: {stats['total_errors']}")
        logger.info(f"Unique error types: {stats['unique_errors']}")
        logger.info("Error counts by type:")
        for error_type, count in stats["error_counts"].items():
            logger.info(f"  {error_type}: {count}")

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
