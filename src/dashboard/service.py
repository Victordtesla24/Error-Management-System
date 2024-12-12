"""Dashboard service module."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard service for managing system monitoring and visualization."""

    def __init__(self):
        """Initialize dashboard service."""
        self.setup_logging()
        self._lock = asyncio.Lock()
        self.agents = {}
        self.projects = {}
        self.notifications = []
        self.background_tasks = set()
        self.running = False

    def setup_logging(self):
        """Set up logging for dashboard service."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure file handler
        fh = logging.FileHandler(log_dir / "dashboard.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)

        # Add handler if not already added
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)

    @classmethod
    async def create(cls) -> "DashboardService":
        """Create and initialize a new dashboard service instance."""
        service = cls()
        await service.start()
        return service

    async def start(self):
        """Start the dashboard service."""
        try:
            async with self._lock:
                self.running = True
                logger.info("Dashboard service started")
                # Start background monitoring
                await self.start_background_tasks()
        except Exception as e:
            logger.error(f"Failed to start dashboard service: {e}")
            raise

    async def stop(self):
        """Stop the dashboard service."""
        try:
            async with self._lock:
                self.running = False
                await self.stop_background_tasks()
                logger.info("Dashboard service stopped")
        except Exception as e:
            logger.error(f"Failed to stop dashboard service: {e}")
            raise

    async def get_system_status(self) -> Dict:
        """Get current system status."""
        try:
            async with self._lock:
                status = {
                    "status": "operational" if self.running else "stopped",
                    "active_agents": len(
                        [a for a in self.agents.values() if a["status"] == "active"]
                    ),
                    "active_projects": len(self.projects),
                    "last_update": datetime.now().isoformat(),
                }
                logger.debug(f"System status: {status}")
                return status
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_metrics(self) -> Dict:
        """Get system metrics."""
        try:
            import psutil

            metrics = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "timestamp": datetime.now().isoformat(),
            }
            logger.debug(f"System metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def add_notification(self, message: str, level: str = "info"):
        """Add a notification."""
        async with self._lock:
            self.notifications.append(
                {
                    "id": str(uuid4()),
                    "message": message,
                    "level": level,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def get_notifications(self) -> List[Dict]:
        """Get all notifications."""
        async with self._lock:
            return self.notifications

    async def create_agent(
        self, name: str, agent_type: str, capabilities: List[str], **kwargs
    ) -> Dict:
        """Create a new agent."""
        agent = {
            "id": str(uuid4()),
            "name": name,
            "type": agent_type,
            "role": agent_type,
            "capabilities": capabilities,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            **kwargs,
        }
        async with self._lock:
            self.agents[agent["id"]] = agent
        return agent

    async def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get agent information."""
        async with self._lock:
            return self.agents.get(agent_id)

    async def create_project(self, name: str, path: str, config: Dict) -> Dict:
        """Create a new project."""
        if not name or not path:
            raise ValueError("Project name and path are required")

        project = {
            "id": str(uuid4()),
            "name": name,
            "path": path,
            "config": config,
            "created_at": datetime.now().isoformat(),
        }
        async with self._lock:
            self.projects[project["id"]] = project
        return project

    async def start_background_tasks(self, monitoring_interval: float = 60):
        """Start background monitoring tasks."""
        task = asyncio.create_task(self._monitor_loop(monitoring_interval))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)

    async def stop_background_tasks(self):
        """Stop all background tasks."""
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()

    async def _monitor_loop(self, interval: float):
        """Background monitoring loop."""
        while self.running:
            try:
                await self.monitor_agents()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

    async def monitor_agents(self) -> Dict:
        """Monitor agent status."""
        async with self._lock:
            now = datetime.now()
            active = 0
            inactive = 0

            for agent in self.agents.values():
                last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
                if (now - last_heartbeat).total_seconds() > 300:  # 5 minutes timeout
                    agent["status"] = "inactive"
                    inactive += 1
                else:
                    agent["status"] = "active"
                    active += 1

            return {
                "status": "ok" if inactive == 0 else "warning",
                "active_agents": active,
                "inactive_agents": inactive,
                "timestamp": now.isoformat(),
            }
