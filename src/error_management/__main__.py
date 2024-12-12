"""Error management system main entry point."""

import asyncio
import logging
from pathlib import Path

from .error_manager import ErrorManager


async def main():
    """Main entry point."""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("logs/error_management.log"),
                logging.StreamHandler(),
            ],
        )
        logger = logging.getLogger("error_management")
        logger.info("Logging initialized at level INFO")
        logger.info("Log file: %s", Path("logs/error_management.log").absolute())

        # Create error manager
        project_path = Path.cwd()
        error_manager = ErrorManager(project_path)

        # Start error manager
        await error_manager.start()

        # Keep running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Failed to start error management system: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
