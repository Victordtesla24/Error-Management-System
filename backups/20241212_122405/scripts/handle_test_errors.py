#!/usr/bin/env python3
"""Script to handle pandas test file errors."""

import logging
import sys
import uuid
from pathlib import Path

from src.error_management.config import ConfigManager
from src.error_management.error_manager import ErrorManager
from src.error_management.error_report import ErrorReport
from src.error_management.models import Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Define the pandas test errors we detected
PANDAS_TEST_ERRORS = [
    # test_dt_accessor.py style errors
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 313,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 325,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 341,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 379,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 394,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 406,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 414,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 425,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 437,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 447,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 457,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 529,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 571,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 590,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 601,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 607,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 620,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 640,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 650,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 658,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 686,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 706,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 712,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 720,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 731,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 757,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 764,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 799,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 811,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 83,
        "type": "Style",
    },
    # test_dt_accessor.py logic errors
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 90,
        "type": "Logic",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_dt_accessor.py",
        "line": 89,
        "type": "Logic",
    },
    # test_str_accessor.py style errors
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_str_accessor.py",
        "line": 8,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_str_accessor.py",
        "line": 21,
        "type": "Style",
    },
    # test_list_accessor.py style errors
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 24,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 34,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 52,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 62,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 72,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 87,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 110,
        "type": "Style",
    },
    {
        "file": "venv/lib/python3.11/site-packages/pandas/tests/series/accessors/test_list_accessor.py",
        "line": 123,
        "type": "Style",
    },
]


async def main():
    """Main function to handle test errors."""
    try:
        # Initialize error manager with project root
        project_root = Path(__file__).parent.parent
        error_manager = ErrorManager(project_root)

        # Load configuration
        config = ConfigManager.load_config("error_management_config.yaml")
        logger.info("Loaded error management configuration")

        # Enable virtual environment monitoring
        if error_manager._secure_env:
            logger.info("Enabling virtual environment monitoring...")
            error_manager._secure_env.enable_venv_monitoring()

        # Add pandas test errors to the error manager
        logger.info("Adding pandas test errors to error manager...")
        added_count = 0
        for error_info in PANDAS_TEST_ERRORS:
            try:
                error = Error(
                    id=str(uuid.uuid4()),
                    file_path=Path(project_root / error_info["file"]).resolve(),
                    line_number=error_info["line"],
                    error_type=error_info["type"],
                    message=f"{error_info['type']} error in pandas test file",
                )
                if error_manager.add_error(error):
                    added_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to add error for {error_info['file']} line {error_info['line']}: {e}"
                )

        logger.info(f"Successfully added {added_count} errors")

        # Initialize error report generator
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_generator = ErrorReport(output_dir=reports_dir)

        # Get current errors
        current_errors = error_manager.get_current_errors()
        logger.info(f"Found {len(current_errors)} current errors")

        # Generate error report
        report_path = report_generator.generate_report(current_errors)
        logger.info(f"Generated error report at: {report_path}")

        # Generate and log summary
        summary = report_generator.generate_summary(current_errors)
        logger.info("\nError Summary:\n" + summary)

        # Process style errors in test files
        test_file_errors = {
            error_id: error
            for error_id, error in current_errors.items()
            if "test_" in str(error.file_path)
            and error.error_type.lower() in ["style", "logic"]
        }

        if test_file_errors:
            logger.info(f"\nProcessing {len(test_file_errors)} test file errors...")

            for error_id, error in test_file_errors.items():
                # Process each error
                result = await error_manager.process_error(error_id)
                if result:
                    logger.info(f"Processed error: {error_id}")
                else:
                    logger.warning(f"Failed to process error: {error_id}")

        logger.info("\nError handling complete")

        # Disable virtual environment monitoring
        if error_manager._secure_env:
            logger.info("Disabling virtual environment monitoring...")
            error_manager._secure_env.disable_venv_monitoring()

    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
