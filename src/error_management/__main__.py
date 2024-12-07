"""
Main Entry Point for Error Management System
Handles system initialization and lifecycle management
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from .error_manager import ErrorManager
from .file_monitor import FileMonitor
from .secure_environment import SecureEnvironment, SecurityError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)
logger = logging.getLogger(__name__)


class ErrorManagementSystem:
    """
    Main system class that coordinates all components
    """

    def __init__(self, project_path: str):
        """
        Initialize the error management system

        Args:
            project_path: Path to the project directory
        """
        self.secure_env: Optional[SecureEnvironment] = None
        self.error_manager: Optional[ErrorManager] = None
        self.file_monitor: Optional[FileMonitor] = None
        self.project_path = project_path
        self._shutdown_event = asyncio.Event()

        # Setup signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

        logger.info("Error Management System initialized")

    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Received signal {signum}")
        if not self._shutdown_event.is_set():
            self._shutdown_event.set()

    async def initialize(self):
        """Initialize system components"""
        try:
            # Initialize secure environment
            self.secure_env = SecureEnvironment(self.project_path)
            logger.info("Secure environment initialized")

            # Initialize error manager
            self.error_manager = ErrorManager(self.secure_env)
            logger.info("Error manager initialized")

            # Initialize file monitor
            self.file_monitor = FileMonitor(self.secure_env, self.error_manager)
            logger.info("File monitor initialized")

        except SecurityError as e:
            logger.error(f"Security error during initialization: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            raise

    async def start(self):
        """Start the error management system"""
        try:
            if not all([self.secure_env, self.error_manager, self.file_monitor]):
                await self.initialize()

            # Start components
            monitor_task = asyncio.create_task(self.file_monitor.start_monitoring())
            error_task = asyncio.create_task(self.error_manager.start_monitoring())

            logger.info("Error Management System started")

            # Wait for shutdown signal
            await self._shutdown_event.wait()

            # Cleanup
            await self.shutdown()

            # Cancel tasks
            monitor_task.cancel()
            error_task.cancel()

            try:
                await asyncio.gather(monitor_task, error_task)
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"Error during system operation: {str(e)}")
            await self.shutdown()
            raise

    async def shutdown(self):
        """Shutdown the error management system"""
        logger.info("Shutting down Error Management System")

        try:
            # Stop file monitor
            if self.file_monitor:
                await self.file_monitor.stop_monitoring()

            # Stop error manager
            if self.error_manager:
                await self.error_manager.stop_monitoring()

            logger.info("Error Management System shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            raise


def validate_arguments():
    """Validate command line arguments"""
    if len(sys.argv) != 2:
        print("Usage: python -m error_management <project_path>")
        sys.exit(1)

    project_path = Path(sys.argv[1])
    if not project_path.exists() or not project_path.is_dir():
        msg = f"Error: {project_path} does not exist " "or is not a directory"
        print(msg)
        sys.exit(1)

    return str(project_path)


async def main():
    """Main entry point"""
    try:
        # Validate command line arguments
        project_path = validate_arguments()

        # Create and start system
        system = ErrorManagementSystem(project_path)
        await system.start()

    except SecurityError as e:
        logger.error(f"Security error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
