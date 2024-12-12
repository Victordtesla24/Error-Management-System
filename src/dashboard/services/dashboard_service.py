"""Dashboard service for managing UI state and data."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.error_management.error_manager import ErrorManager
from src.error_management.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class DashboardService:
    def __init__(
        self,
        error_manager: Optional[ErrorManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        self.errors = []
        self.metrics = {
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "error_count": 0,
            "success_rate": 100.0,
            "last_update": datetime.now().isoformat(),
        }
        self.notifications = []
        self.error_manager = error_manager
        self.metrics_collector = metrics_collector
        self._update_task = None
        self._running = False
        self._last_error_count = 0

    async def start(self):
        """Start the dashboard service."""
        self._running = True
        # Initial state update
        await self._update_state()
        # Start background update loop
        self._update_task = asyncio.create_task(self._update_loop())

    async def stop(self):
        """Stop the dashboard service."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None

    async def _update_loop(self):
        """Background task to update dashboard state."""
        try:
            while self._running:
                await self._update_state()
                await asyncio.sleep(0.1)  # Update more frequently for testing
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in update loop: {e}")
            # Add error notification
            self.add_notification(
                {
                    "type": "Error",
                    "message": f"Update loop error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def _update_state(self):
        """Update dashboard state from various sources."""
        try:
            # Update errors if error manager is available
            if self.error_manager:
                errors = await self.error_manager.get_errors()
                self.errors = [
                    {
                        "id": error_id,
                        "file": str(error.file_path),
                        "line": error.line_number,
                        "type": error.error_type,
                        "message": error.message,
                        "status": error.status,
                        "timestamp": (
                            error.created_at.isoformat()
                            if hasattr(error, "created_at")
                            else datetime.now().isoformat()
                        ),
                    }
                    for error_id, error in errors.items()
                ]

                # Check for new errors
                current_error_count = len(self.errors)
                if current_error_count > self._last_error_count:
                    # Add notification for new errors
                    new_errors = current_error_count - self._last_error_count
                    self.add_notification(
                        {
                            "type": "Error",
                            "message": f"New errors detected: {new_errors}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                self._last_error_count = current_error_count

            # Update metrics if metrics collector is available
            if self.metrics_collector:
                try:
                    metrics = self.metrics_collector.collect_metrics()
                    self.metrics.update(
                        {
                            "memory_usage": metrics.memory_usage,
                            "cpu_usage": metrics.cpu_usage,
                            "error_count": len(self.errors),
                            "success_rate": metrics.success_rate,
                            "last_update": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                    self.add_notification(
                        {
                            "type": "Warning",
                            "message": f"Metrics collection error: {str(e)}",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        except Exception as e:
            logger.error(f"Error updating dashboard state: {e}")
            self.add_notification(
                {
                    "type": "Error",
                    "message": f"State update error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_notification(self, notification: Dict[str, Any]):
        """Add a new notification."""
        try:
            if not isinstance(notification, dict):
                raise ValueError("Notification must be a dictionary")

            required_fields = ["type", "message", "timestamp"]
            for field in required_fields:
                if field not in notification:
                    raise ValueError(f"Notification missing required field: {field}")

            self.notifications.append(notification)
            # Keep only last 100 notifications
            self.notifications = self.notifications[-100:]

            logger.info(f"Added notification: {notification['message']}")
        except Exception as e:
            logger.error(f"Error adding notification: {e}")

    async def get_active_errors(self) -> List[Dict[str, Any]]:
        """Get list of active errors."""
        try:
            # Force state update before returning errors
            await self._update_state()
            return self.errors
        except Exception as e:
            logger.error(f"Error fetching active errors: {e}")
            return []

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Force state update before returning metrics
            await self._update_state()
            return self.metrics
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return {}

    async def get_notifications(self) -> List[Dict[str, Any]]:
        """Get current notifications."""
        try:
            return self.notifications
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []
