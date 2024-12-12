"""Agent metrics and monitoring module."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import streamlit as st

from src.error_management.memory_manager import MemoryManager
from src.error_management.metrics import MetricsCollector
from src.error_management.service import ErrorManagementService


class AgentMetricsCollector:
    """Collect and manage agent metrics."""

    def __init__(
        self, memory_manager: MemoryManager, error_service: ErrorManagementService
    ):
        """Initialize metrics collector."""
        self._memory_manager = memory_manager
        self._error_service = error_service
        self._metrics_collector = MetricsCollector()
        self._process = psutil.Process()
        self._previous_metrics = None
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Initialize session state if not exists
        if not hasattr(st.session_state, "agent_metrics"):
            st.session_state.agent_metrics = {}
        if not hasattr(st.session_state, "agent_logs"):
            st.session_state.agent_logs = {}
        if not hasattr(st.session_state, "agent_activities"):
            st.session_state.agent_activities = {}
        if not hasattr(st.session_state, "agent_security"):
            st.session_state.agent_security = {}
        if not hasattr(st.session_state, "agents"):
            st.session_state.agents = []

    def update_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Update agent metrics with real data."""
        metrics = st.session_state.agent_metrics.get(agent_id, {})
        agent = next((a for a in st.session_state.agents if a["id"] == agent_id), None)

        if agent and agent.get("status") == "running":
            # Get system metrics
            system_metrics = self._metrics_collector.collect_metrics()

            # Update metrics with real data
            metrics.update(
                {
                    "cpu_usage": system_metrics.cpu_usage,
                    "memory_usage": system_metrics.memory_usage,
                    "response_time": system_metrics.response_time,
                    "success_rate": system_metrics.success_rate,
                    "active_time": metrics.get("active_time", 0) + 1,
                    "errors_fixed": 0,
                    "avg_response_time": 0,
                }
            )

            try:
                # Get error statistics
                future = asyncio.run_coroutine_threadsafe(
                    self._error_service.get_errors_async(), self._loop
                )
                errors = future.result(timeout=5)
                if errors:
                    fixed_errors = [e for e in errors if e.status == "fixed"]
                    metrics["errors_fixed"] = len(fixed_errors)
                    if fixed_errors:
                        metrics["avg_response_time"] = sum(
                            e.fix_time for e in fixed_errors if e.fix_time
                        ) / len(fixed_errors)

                # Get container metrics
                container_metrics = self._get_container_metrics()
                metrics.update(container_metrics)

                # Update security metrics
                security_metrics = self._get_security_metrics()
                if agent_id not in st.session_state.agent_security:
                    st.session_state.agent_security[agent_id] = {}
                st.session_state.agent_security[agent_id].update(security_metrics)

                # Add system logs
                self._update_logs(agent_id)

            except Exception as e:
                if agent_id not in st.session_state.agent_logs:
                    st.session_state.agent_logs[agent_id] = []
                st.session_state.agent_logs[agent_id].append(
                    {
                        "timestamp": datetime.now(),
                        "level": "ERROR",
                        "message": f"Failed to update metrics: {str(e)}",
                    }
                )

            # Store metrics
            st.session_state.agent_metrics[agent_id] = metrics

        return metrics

    def _get_container_metrics(self) -> Dict[str, float]:
        """Get container resource usage metrics."""
        return {
            "container_cpu": self._process.cpu_percent(),
            "container_memory": self._process.memory_percent(),
            "container_threads": self._process.num_threads(),
            "container_handles": (
                self._process.num_handles()
                if hasattr(self._process, "num_handles")
                else 0
            ),
            "container_connections": len(self._process.connections()),
        }

    def _get_security_metrics(self) -> Dict[str, Any]:
        """Get security-related metrics."""
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._error_service.scan_security_async(), self._loop
            )
            security_scan = future.result(timeout=5)
            return {
                "permissions": ["read", "write", "execute"],
                "vulnerabilities_detected": (
                    security_scan.vulnerabilities if security_scan else 0
                ),
                "security_score": security_scan.score if security_scan else 100,
                "last_security_scan": datetime.now(),
            }
        except Exception:
            return {
                "permissions": ["read", "write", "execute"],
                "vulnerabilities_detected": 0,
                "security_score": 100,
                "last_security_scan": datetime.now(),
            }

    def _update_logs(self, agent_id: str) -> None:
        """Update agent logs with system events."""
        if agent_id not in st.session_state.agent_logs:
            st.session_state.agent_logs[agent_id] = []

        try:
            # Get logs from error service
            future = asyncio.run_coroutine_threadsafe(
                self._error_service.get_logs_async(), self._loop
            )
            service_logs = future.result(timeout=5)
            if service_logs:
                for log in service_logs:
                    st.session_state.agent_logs[agent_id].append(
                        {
                            "timestamp": datetime.now(),
                            "level": log.level,
                            "message": log.message,
                        }
                    )

                # Trim logs to keep only last 1000 entries
                st.session_state.agent_logs[agent_id] = st.session_state.agent_logs[
                    agent_id
                ][-1000:]
        except Exception as e:
            st.session_state.agent_logs[agent_id].append(
                {
                    "timestamp": datetime.now(),
                    "level": "ERROR",
                    "message": f"Failed to update logs: {str(e)}",
                }
            )

    def log_agent_activity(
        self,
        agent_id: str,
        activity_type: str,
        status: str,
        details: str,
        project: Optional[str] = None,
    ) -> None:
        """Log an agent activity."""
        activity = {
            "timestamp": datetime.now(),
            "type": activity_type,
            "status": status,
            "details": details,
        }
        if project:
            activity["project"] = project

        if agent_id not in st.session_state.agent_activities:
            st.session_state.agent_activities[agent_id] = []

        st.session_state.agent_activities[agent_id].insert(0, activity)

        # Trim activities to keep only last 1000 entries
        st.session_state.agent_activities[agent_id] = st.session_state.agent_activities[
            agent_id
        ][:1000]

    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get current metrics for an agent."""
        return self.update_agent_metrics(agent_id)

    def get_agent_security(self, agent_id: str) -> Dict[str, Any]:
        """Get security metrics for an agent."""
        return st.session_state.agent_security.get(agent_id, {})

    def get_agent_logs(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent logs for an agent."""
        logs = st.session_state.agent_logs.get(agent_id, [])
        return logs[-limit:] if logs else []

    def get_agent_activities(
        self, agent_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get activities for an agent."""
        activities = st.session_state.agent_activities.get(agent_id, [])
        return activities[:limit]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        metrics = self._metrics_collector.collect_metrics()
        return {
            "cpu": {
                "usage": metrics.cpu_usage,
                "cores": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            },
            "memory": {
                "usage": metrics.memory_usage,
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
            },
            "disk": {
                "usage": psutil.disk_usage("/").percent,
                "read_bytes": (
                    psutil.disk_io_counters().read_bytes
                    if psutil.disk_io_counters()
                    else 0
                ),
                "write_bytes": (
                    psutil.disk_io_counters().write_bytes
                    if psutil.disk_io_counters()
                    else 0
                ),
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv,
            },
            "response_time": metrics.response_time,
            "success_rate": metrics.success_rate,
        }
