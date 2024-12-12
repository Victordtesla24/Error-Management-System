"""Memory management module."""

import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import psutil


@dataclass
class ResourceThreshold:
    """Resource threshold configuration."""

    cpu_percent: float = 80.0
    memory_percent: float = 80.0
    disk_percent: float = 80.0


@dataclass
class ResourceUsage:
    """Resource usage information."""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: float


class MemoryManager:
    """Manage system resources and memory."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize memory manager."""
        self._project_path = project_path or Path.cwd()
        self._thresholds = ResourceThreshold()
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._current_usage: Optional[ResourceUsage] = None
        self._lock = threading.Lock()

        # Set up logging
        self.logger = logging.getLogger("memory_manager")
        self.logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Add file handler
        fh = logging.FileHandler(logs_dir / "memory_manager.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_resources,
            daemon=True,
            name="memory_monitor",
        )
        self._monitor_thread.start()
        self.logger.info("Starting memory monitoring")

    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        if self._monitor_thread:
            self._stop_event.set()
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
            self.logger.info("Memory monitoring stopped")

    def get_current_usage(self) -> Optional[ResourceUsage]:
        """Get current resource usage."""
        with self._lock:
            return self._current_usage

    def set_thresholds(self, thresholds: ResourceThreshold) -> None:
        """Set resource thresholds."""
        with self._lock:
            self._thresholds = thresholds
            self.logger.info(f"Resource thresholds updated: {thresholds}")

    def _monitor_resources(self) -> None:
        """Monitor system resources."""
        while not self._stop_event.is_set():
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)

                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # Get disk usage
                disk = psutil.disk_usage(str(self._project_path))
                disk_percent = disk.percent

                # Update current usage
                with self._lock:
                    self._current_usage = ResourceUsage(
                        cpu_percent=cpu_percent,
                        memory_percent=memory_percent,
                        disk_percent=disk_percent,
                        timestamp=time.time(),
                    )

                # Check thresholds
                self._check_thresholds()

                # Sleep before next check
                time.sleep(5)

            except Exception as e:
                self.logger.error(f"Error monitoring resources: {str(e)}")
                time.sleep(10)  # Wait longer on error

    def _check_thresholds(self) -> None:
        """Check if resource usage exceeds thresholds."""
        if not self._current_usage:
            return

        # Check CPU usage
        if self._current_usage.cpu_percent > self._thresholds.cpu_percent:
            self.logger.warning(
                f"CPU usage ({self._current_usage.cpu_percent}%) exceeds threshold "
                f"({self._thresholds.cpu_percent}%)"
            )

        # Check memory usage
        if self._current_usage.memory_percent > self._thresholds.memory_percent:
            self.logger.warning(
                f"Memory usage ({self._current_usage.memory_percent}%) exceeds threshold "
                f"({self._thresholds.memory_percent}%)"
            )

        # Check disk usage
        if self._current_usage.disk_percent > self._thresholds.disk_percent:
            self.logger.warning(
                f"Disk usage ({self._current_usage.disk_percent}%) exceeds threshold "
                f"({self._thresholds.disk_percent}%)"
            )

    def get_memory_stats(self) -> Dict[str, float]:
        """Get detailed memory statistics."""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total / (1024 * 1024 * 1024),  # GB
                "available": memory.available / (1024 * 1024 * 1024),  # GB
                "used": memory.used / (1024 * 1024 * 1024),  # GB
                "percent": memory.percent,
            }
        except Exception as e:
            self.logger.error(f"Error getting memory stats: {str(e)}")
            return {
                "total": 0.0,
                "available": 0.0,
                "used": 0.0,
                "percent": 0.0,
            }

    def get_cpu_stats(self) -> Dict[str, float]:
        """Get detailed CPU statistics."""
        try:
            return {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0.0,
            }
        except Exception as e:
            self.logger.error(f"Error getting CPU stats: {str(e)}")
            return {
                "percent": 0.0,
                "count": 0,
                "frequency": 0.0,
            }

    def get_disk_stats(self) -> Dict[str, float]:
        """Get detailed disk statistics."""
        try:
            disk = psutil.disk_usage(str(self._project_path))
            return {
                "total": disk.total / (1024 * 1024 * 1024),  # GB
                "used": disk.used / (1024 * 1024 * 1024),  # GB
                "free": disk.free / (1024 * 1024 * 1024),  # GB
                "percent": disk.percent,
            }
        except Exception as e:
            self.logger.error(f"Error getting disk stats: {str(e)}")
            return {
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0,
            }
