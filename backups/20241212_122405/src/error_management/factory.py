"""Service factory module."""

import logging
from pathlib import Path
from typing import Tuple

from .error_handler import ErrorHandler
from .memory_manager import MemoryManager
from .metrics import MetricsCollector
from .service import ErrorManagementService


class ServiceFactory:
    """Factory for creating services."""

    @staticmethod
    def create_all_services(
        project_path: Path,
    ) -> Tuple[MemoryManager, MetricsCollector, ErrorManagementService]:
        """Create all required services."""
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
            logger = logging.getLogger("service_factory")
            logger.info("Creating services...")

            # Create memory manager
            memory_manager = MemoryManager()
            logger.info("Created memory manager")

            # Create metrics collector
            metrics_collector = MetricsCollector()
            logger.info("Created metrics collector")

            # Create error management service
            error_service = ErrorManagementService(project_path)
            logger.info("Created error management service")

            return memory_manager, metrics_collector, error_service

        except Exception as e:
            logger.error(f"Failed to create services: {str(e)}")
            raise

    @staticmethod
    def create_error_handler() -> ErrorHandler:
        """Create error handler."""
        try:
            logger = logging.getLogger("service_factory")
            handler = ErrorHandler()
            logger.info("Created error handler")
            return handler
        except Exception as e:
            logger.error(f"Failed to create error handler: {str(e)}")
            raise

    @staticmethod
    def create_memory_manager() -> MemoryManager:
        """Create memory manager."""
        try:
            logger = logging.getLogger("service_factory")
            manager = MemoryManager()
            logger.info("Created memory manager")
            return manager
        except Exception as e:
            logger.error(f"Failed to create memory manager: {str(e)}")
            raise

    @staticmethod
    def create_metrics_collector() -> MetricsCollector:
        """Create metrics collector."""
        try:
            logger = logging.getLogger("service_factory")
            collector = MetricsCollector()
            logger.info("Created metrics collector")
            return collector
        except Exception as e:
            logger.error(f"Failed to create metrics collector: {str(e)}")
            raise

    @staticmethod
    def create_error_service(project_path: Path) -> ErrorManagementService:
        """Create error management service."""
        try:
            logger = logging.getLogger("service_factory")
            service = ErrorManagementService(project_path)
            logger.info("Created error management service")
            return service
        except Exception as e:
            logger.error(f"Failed to create error service: {str(e)}")
            raise
