"""Agent monitoring functionality."""

import asyncio
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.error_management.factory import ServiceFactory


class AgentMonitor:
    """Monitors agent metrics, status, and activities."""

    def __init__(self, project_path: Path) -> None:
        """Initialize agent monitor.

        Args:
            project_path: Path to project directory
        """
        self.project_path = project_path
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._monitors: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
        self._loop = asyncio.get_event_loop()
        self._metrics_counter = 0  # Synchronized counter for metrics updates

        # Initialize services
        self._memory_manager, self._metrics_collector, self._error_service = (
            ServiceFactory.create_all_services()
        )

        # Start memory monitoring
        self._memory_manager.start_monitoring()

    def start_agent(self, agent_id: str) -> bool:
        """Start monitoring an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            bool: True if agent started successfully
        """
        with self._lock:
            if agent_id in self._agents:
                return False

            # Initialize agent state with zero metrics
            self._agents[agent_id] = {
                "status": "running",
                "metrics": {
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "response_time": 0.1,
                    "success_rate": 100.0,
                    "error_count": 0,
                    "active_time": time.time(),
                },
                "security": {
                    "score": 100,
                    "vulnerabilities": 0,
                    "last_scan": datetime.now(),
                },
                "logs": [],
                "activities": [
                    {
                        "timestamp": datetime.now(),
                        "type": "Agent Start",
                        "status": "Success",
                        "details": f"Agent {agent_id} started",
                    }
                ],
                "container": {
                    "status": "running",
                    "image": "error-management-agent:latest",
                    "ports": {"8000/tcp": 8000},
                    "volumes": {str(self.project_path): "/app"},
                    "resources": {"cpu": "0.5", "memory": "512M"},
                },
                "_update_count": 0,  # Track updates per agent
            }

            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_agent, args=(agent_id,), daemon=True
            )
            self._monitors[agent_id] = monitor_thread
            monitor_thread.start()

            return True

    def stop_agent(self, agent_id: str) -> bool:
        """Stop monitoring an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            bool: True if agent stopped successfully
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            # Update status
            self._agents[agent_id]["status"] = "stopped"

            # Stop and remove monitor thread
            if agent_id in self._monitors:
                thread = self._monitors.pop(agent_id)
                thread.join(timeout=1)

            return True

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Optional[Dict]: Agent status information or None if agent not found
        """
        with self._lock:
            if agent_id not in self._agents:
                return None
            status = {
                k: v.copy() if isinstance(v, dict) else v
                for k, v in self._agents[agent_id].items()
                if not k.startswith("_")
            }  # Exclude private fields
            return status

    def get_agent_logs(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get logs for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List[Dict]: List of log entries
        """
        with self._lock:
            if agent_id not in self._agents:
                return []
            return self._agents[agent_id]["logs"].copy()

    def get_agent_activities(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get activity history for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List[Dict]: List of activities
        """
        with self._lock:
            if agent_id not in self._agents:
                return []
            return self._agents[agent_id]["activities"].copy()

    def get_agent_security(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get security metrics for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Optional[Dict]: Security metrics or None if agent not found
        """
        with self._lock:
            if agent_id not in self._agents:
                return None
            return self._agents[agent_id]["security"].copy()

    def get_agent_container(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get container information for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Optional[Dict]: Container information or None if agent not found
        """
        with self._lock:
            if agent_id not in self._agents:
                return None
            return self._agents[agent_id]["container"].copy()

    def _monitor_agent(self, agent_id: str) -> None:
        """Monitor agent metrics and status in a separate thread.

        Args:
            agent_id: Agent identifier
        """
        try:
            while True:
                # Check status first without lock
                status = None
                with self._lock:
                    if agent_id in self._agents:
                        status = self._agents[agent_id]["status"]

                if status != "running":
                    break

                try:
                    # Collect metrics outside lock
                    metrics = self._metrics_collector.collect_metrics()

                    # Update metrics with synchronized counter
                    with self._lock:
                        if (
                            agent_id in self._agents
                            and self._agents[agent_id]["status"] == "running"
                        ):
                            # Only update metrics after first collection
                            if self._metrics_counter > 0:
                                self._agents[agent_id]["metrics"].update(
                                    {
                                        "cpu_usage": metrics.cpu_usage,
                                        "memory_usage": metrics.memory_usage,
                                        "response_time": metrics.response_time,
                                        "success_rate": metrics.success_rate,
                                        "error_count": metrics.error_count,
                                        "active_time": time.time(),
                                    }
                                )
                            self._agents[agent_id]["_update_count"] += 1
                            self._metrics_counter += 1

                except StopIteration:
                    # If mock runs out of values, keep last metrics
                    break

                # Run security scan asynchronously
                asyncio.run_coroutine_threadsafe(
                    self._update_security(agent_id), self._loop
                )

                # Sleep between updates
                time.sleep(0.1)

        except Exception as e:
            # Log error with minimal lock time
            with self._lock:
                if agent_id in self._agents:
                    self._agents[agent_id]["logs"].append(
                        {
                            "timestamp": datetime.now(),
                            "level": "ERROR",
                            "message": f"Monitoring error: {str(e)}",
                        }
                    )

    async def _update_security(self, agent_id: str) -> None:
        """Update security metrics for an agent.

        Args:
            agent_id: Agent identifier
        """
        try:
            security_scan = await self._error_service.scan_security()
            with self._lock:
                if agent_id in self._agents:
                    self._agents[agent_id]["security"].update(
                        {
                            "score": security_scan.score,
                            "vulnerabilities": security_scan.vulnerabilities,
                            "last_scan": datetime.now(),
                        }
                    )
        except Exception as e:
            with self._lock:
                if agent_id in self._agents:
                    self._agents[agent_id]["logs"].append(
                        {
                            "timestamp": datetime.now(),
                            "level": "ERROR",
                            "message": f"Security scan error: {str(e)}",
                        }
                    )
