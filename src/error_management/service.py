"""Error management service with Sentry integration."""

import logging
import logging.config  # Add explicit import for logging.config
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import sentry_sdk
import structlog
import yaml
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

from .error_handler import error_handler
from .monitor import start_monitoring


class ErrorManagementService:
    """Main error management service."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize error management service."""
        self.project_path = project_path or Path.cwd()
        self.logger = structlog.get_logger()
        self.config = self._load_config()
        self._initialize_logging()
        self._initialize_sentry()
        self._initialize_error_handler()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        try:
            config_path = self.project_path / "src" / "error_management" / "config.yaml"
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error("Failed to load config", error=str(e))
            return {}

    def _initialize_logging(self) -> None:
        """Initialize logging configuration."""
        try:
            logging_config = self.config.get("logging", {})
            logging.config.dictConfig(logging_config)
            self.logger.info(
                "Logging initialized", level=logging_config.get("root", {}).get("level")
            )
        except Exception as e:
            self.logger.error("Failed to initialize logging", error=str(e))

    def _initialize_sentry(self) -> None:
        """Initialize Sentry integration."""
        try:
            sentry_config = self.config.get("error_management", {}).get(
                "error_tracking", {}
            )

            # Get DSN from environment or use a default value
            dsn = os.getenv("SENTRY_DSN")
            if not dsn:
                self.logger.warning(
                    "SENTRY_DSN environment variable not set, skipping Sentry initialization"
                )
                return

            # Initialize Sentry with integrations
            sentry_sdk.init(
                dsn=dsn,
                environment=sentry_config.get("environment", "development"),
                traces_sample_rate=sentry_config.get("traces_sample_rate", 1.0),
                profiles_sample_rate=sentry_config.get("profiles_sample_rate", 1.0),
                attach_stacktrace=sentry_config.get("attach_stacktrace", True),
                debug=sentry_config.get("debug", False),
                integrations=[
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                    ThreadingIntegration(propagate_hub=True),
                ],
                before_send=self._before_send_event,
            )
            self.logger.info("Sentry initialized")
        except Exception as e:
            self.logger.error("Failed to initialize Sentry", error=str(e))

    def _initialize_error_handler(self) -> None:
        """Initialize error handler."""
        try:
            error_config = self.config.get("error_management", {})

            # Configure error handler
            error_handler.project_path = self.project_path

            # Add monitored paths
            monitored_paths = error_config.get("monitoring", {}).get("paths", [])
            for path in monitored_paths:
                full_path = self.project_path / path
                error_handler.monitor(full_path)

            self.logger.info("Error handler initialized")
        except Exception as e:
            self.logger.error("Failed to initialize error handler", error=str(e))

    def _before_send_event(
        self, event: Dict[str, Any], hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process event before sending to Sentry."""
        try:
            # Add custom context
            event.setdefault("contexts", {}).update(
                {
                    "project": {
                        "name": "error-management-system",
                        "path": str(self.project_path),
                    },
                    "error_stats": error_handler.get_error_stats(),
                }
            )

            return event
        except Exception as e:
            self.logger.error("Error processing Sentry event", error=str(e))
            return event

    def start(self) -> None:
        """Start error management service."""
        try:
            self.logger.info("Starting error management service")

            # Start file monitoring
            if (
                self.config.get("error_management", {})
                .get("monitoring", {})
                .get("enabled", True)
            ):
                start_monitoring(self.project_path)

            self.logger.info("Error management service started")
        except Exception as e:
            self.logger.error("Failed to start error management service", error=str(e))
            raise

    def stop(self) -> None:
        """Stop error management service."""
        try:
            self.logger.info("Stopping error management service")
            # Add cleanup code here
            self.logger.info("Error management service stopped")
        except Exception as e:
            self.logger.error("Failed to stop error management service", error=str(e))
            raise


# Create singleton instance
error_management_service = ErrorManagementService()
