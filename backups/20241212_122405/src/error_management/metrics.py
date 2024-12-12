"""Metrics collection and monitoring module."""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class SystemMetrics:
    """System metrics data."""

    cpu_usage: float
    memory_usage: float
    response_time: float
    success_rate: float
    error_count: int


class MetricsCollector:
    """Collect and monitor system metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.logger = logging.getLogger("metrics_collector")
        self._lock = threading.RLock()
        self._metrics_history: List[Dict[str, float]] = []
        self._start_time = datetime.now()

        # Performance thresholds
        self.cpu_threshold = 80.0  # 80% CPU usage
        self.memory_threshold = 85.0  # 85% memory usage
        self.response_threshold = 1.0  # 1 second

        # Collection settings
        self.history_size = 1000  # Keep last 1000 metrics
        self.collection_interval = 1.0  # 1 second

        # Performance stats
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0,
            "peak_cpu_usage": 0.0,
            "peak_memory_usage": 0.0,
            "last_collection": None,
        }

    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            with self._lock:
                # Get CPU and memory usage
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.Process().memory_percent()

                # Calculate success rate
                total_requests = self._stats["total_requests"]
                success_rate = (
                    (self._stats["successful_requests"] / total_requests * 100)
                    if total_requests > 0
                    else 100.0
                )

                # Create metrics
                metrics = SystemMetrics(
                    cpu_usage=cpu_percent,
                    memory_usage=memory_percent,
                    response_time=self._stats["avg_response_time"],
                    success_rate=success_rate,
                    error_count=self._stats["total_errors"],
                )

                # Update stats
                self._stats["peak_cpu_usage"] = max(
                    self._stats["peak_cpu_usage"], cpu_percent
                )
                self._stats["peak_memory_usage"] = max(
                    self._stats["peak_memory_usage"], memory_percent
                )
                self._stats["last_collection"] = datetime.now()

                # Add to history
                self._add_to_history(
                    {
                        "timestamp": datetime.now().timestamp(),
                        "cpu_usage": cpu_percent,
                        "memory_usage": memory_percent,
                        "response_time": self._stats["avg_response_time"],
                        "success_rate": success_rate,
                        "error_count": self._stats["total_errors"],
                    }
                )

                return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {str(e)}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                response_time=0.0,
                success_rate=100.0,
                error_count=0,
            )

    def _add_to_history(self, metrics: Dict[str, float]) -> None:
        """Add metrics to history."""
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > self.history_size:
            self._metrics_history.pop(0)

    def record_request(self, success: bool, response_time: float) -> None:
        """Record request metrics."""
        try:
            with self._lock:
                self._stats["total_requests"] += 1
                if success:
                    self._stats["successful_requests"] += 1
                else:
                    self._stats["failed_requests"] += 1

                # Update average response time
                total = self._stats["total_requests"]
                current_avg = self._stats["avg_response_time"]
                self._stats["avg_response_time"] = (
                    current_avg * (total - 1) + response_time
                ) / total

        except Exception as e:
            self.logger.error(f"Failed to record request: {str(e)}")

    def record_error(self) -> None:
        """Record error occurrence."""
        try:
            with self._lock:
                self._stats["total_errors"] += 1
        except Exception as e:
            self.logger.error(f"Failed to record error: {str(e)}")

    def get_metrics_history(
        self, minutes: Optional[int] = None
    ) -> List[Dict[str, float]]:
        """Get metrics history."""
        try:
            if not minutes:
                return self._metrics_history

            # Filter by time
            cutoff = time.time() - (minutes * 60)
            return [m for m in self._metrics_history if m["timestamp"] >= cutoff]
        except Exception as e:
            self.logger.error(f"Failed to get metrics history: {str(e)}")
            return []

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        try:
            with self._lock:
                return {
                    "uptime": (datetime.now() - self._start_time).total_seconds(),
                    "total_requests": self._stats["total_requests"],
                    "successful_requests": self._stats["successful_requests"],
                    "failed_requests": self._stats["failed_requests"],
                    "total_errors": self._stats["total_errors"],
                    "avg_response_time": self._stats["avg_response_time"],
                    "peak_cpu_usage": self._stats["peak_cpu_usage"],
                    "peak_memory_usage": self._stats["peak_memory_usage"],
                    "last_collection": self._stats["last_collection"],
                }
        except Exception as e:
            self.logger.error(f"Failed to get performance stats: {str(e)}")
            return {}

    def check_performance_issues(self) -> List[Dict[str, Any]]:
        """Check for performance issues."""
        try:
            issues = []
            metrics = self.collect_metrics()

            # Check CPU usage
            if metrics.cpu_usage > self.cpu_threshold:
                issues.append(
                    {
                        "type": "cpu",
                        "message": f"High CPU usage: {metrics.cpu_usage:.1f}%",
                        "value": metrics.cpu_usage,
                        "threshold": self.cpu_threshold,
                    }
                )

            # Check memory usage
            if metrics.memory_usage > self.memory_threshold:
                issues.append(
                    {
                        "type": "memory",
                        "message": f"High memory usage: {metrics.memory_usage:.1f}%",
                        "value": metrics.memory_usage,
                        "threshold": self.memory_threshold,
                    }
                )

            # Check response time
            if metrics.response_time > self.response_threshold:
                issues.append(
                    {
                        "type": "response_time",
                        "message": f"High response time: {metrics.response_time:.3f}s",
                        "value": metrics.response_time,
                        "threshold": self.response_threshold,
                    }
                )

            return issues

        except Exception as e:
            self.logger.error(f"Failed to check performance issues: {str(e)}")
            return []

    def adjust_thresholds(
        self,
        cpu: Optional[float] = None,
        memory: Optional[float] = None,
        response: Optional[float] = None,
    ) -> None:
        """Adjust performance thresholds."""
        try:
            with self._lock:
                if cpu is not None:
                    self.cpu_threshold = max(0.0, min(100.0, cpu))
                if memory is not None:
                    self.memory_threshold = max(0.0, min(100.0, memory))
                if response is not None:
                    self.response_threshold = max(0.0, response)

            self.logger.info(
                f"Adjusted thresholds - CPU: {self.cpu_threshold}%, "
                f"Memory: {self.memory_threshold}%, "
                f"Response: {self.response_threshold}s"
            )

        except Exception as e:
            self.logger.error(f"Failed to adjust thresholds: {str(e)}")

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        try:
            with self._lock:
                self._stats = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_errors": 0,
                    "avg_response_time": 0.0,
                    "peak_cpu_usage": 0.0,
                    "peak_memory_usage": 0.0,
                    "last_collection": None,
                }
                self._metrics_history.clear()
                self._start_time = datetime.now()

            self.logger.info("Reset performance statistics")

        except Exception as e:
            self.logger.error(f"Failed to reset stats: {str(e)}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            metrics = self.collect_metrics()
            issues = self.check_performance_issues()

            return {
                "status": "healthy" if not issues else "degraded",
                "metrics": {
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "response_time": metrics.response_time,
                    "success_rate": metrics.success_rate,
                    "error_count": metrics.error_count,
                },
                "issues": issues,
                "last_check": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to get system health: {str(e)}")
            return {"status": "unknown", "error": str(e)}
