"""
Dashboard Service Module
Provides web API for system monitoring and control
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict

import psutil
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard service for system monitoring and control"""

    def __init__(self):
        """Initialize dashboard service"""
        self.app = web.Application()
        self.setup_routes()
        self.projects: Dict[str, Dict] = {}
        self.agents: Dict[str, Dict] = {}

    def setup_routes(self):
        """Setup API routes"""
        routes = [
            # System endpoints
            web.get("/api/system/status", self.get_system_status),
            web.get("/api/system/security-metrics", self.get_security_metrics),
            web.get("/api/system/metrics", self.get_metrics),
            # System control endpoints
            web.post("/api/system/start", self.start_system),
            web.post("/api/system/stop", self.stop_system),
            web.post("/api/system/restart", self.restart_system),
            # Project endpoints
            web.get("/api/projects", self.list_projects),
            web.post("/api/projects", self.add_project),
            web.get("/api/projects/{id}/status", self.get_project_status),
            web.delete("/api/projects/{id}", self.remove_project),
            # Agent endpoints
            web.get("/api/agents", self.list_agents),
            web.post("/api/agents", self.create_agent),
            web.get("/api/agents/{id}/status", self.get_agent_status),
            web.delete("/api/agents/{id}", self.remove_agent),
        ]
        self.app.add_routes(routes)

    async def get_system_status(self, request: web.Request) -> web.Response:
        """Get system status"""
        status = {
            "projects": len(self.projects),
            "agents": len(self.agents),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
        }
        return web.json_response(status)

    async def get_security_metrics(self, request: web.Request) -> web.Response:
        """Get security metrics"""
        metrics = {
            "securityScore": 85,
            "activeThreats": 0,
            "certificateStatus": "valid",
        }
        return web.json_response(metrics)

    async def get_metrics(self, request: web.Request) -> web.Response:
        """Get system metrics"""
        metrics = {
            "agent_count": len(self.agents),
            "error_count": 0,
            "fix_time": 0.5,
        }
        return web.json_response(metrics)

    async def start_system(self, request: web.Request) -> web.Response:
        """Start system"""
        return web.json_response({"status": "started"})

    async def stop_system(self, request: web.Request) -> web.Response:
        """Stop system"""
        return web.json_response({"status": "stopped"})

    async def restart_system(self, request: web.Request) -> web.Response:
        """Restart system"""
        return web.json_response({"status": "restarted"})

    async def list_projects(self, request: web.Request) -> web.Response:
        """List all projects"""
        projects = [{"id": pid, **project} for pid, project in self.projects.items()]
        return web.json_response(projects)

    async def add_project(self, request: web.Request) -> web.Response:
        """Add new project"""
        data = await request.json()
        path = data.get("path")

        if not path or not Path(path).exists():
            return web.Response(status=400)

        project_id = str(uuid.uuid4())
        self.projects[project_id] = {"path": path, "status": "active"}

        return web.json_response({"id": project_id, "path": path})

    async def get_project_status(self, request: web.Request) -> web.Response:
        """Get project status"""
        project_id = request.match_info["id"]
        project = self.projects.get(project_id)

        if not project:
            return web.Response(status=404)

        return web.json_response({"id": project_id, **project})

    async def remove_project(self, request: web.Request) -> web.Response:
        """Remove project"""
        project_id = request.match_info["id"]

        if project_id not in self.projects:
            return web.Response(status=404)

        del self.projects[project_id]
        return web.Response(status=200)

    async def list_agents(self, request: web.Request) -> web.Response:
        """List all agents"""
        agents = [{"id": aid, **agent} for aid, agent in self.agents.items()]
        return web.json_response(agents)

    async def create_agent(self, request: web.Request) -> web.Response:
        """Create new agent"""
        agent_id = str(uuid.uuid4())
        self.agents[agent_id] = {"status": "active", "type": "error_monitor"}

        return web.json_response({"id": agent_id, **self.agents[agent_id]})

    async def get_agent_status(self, request: web.Request) -> web.Response:
        """Get agent status"""
        agent_id = request.match_info["id"]
        agent = self.agents.get(agent_id)

        if not agent:
            return web.Response(status=404)

        return web.json_response({"id": agent_id, **agent})

    async def remove_agent(self, request: web.Request) -> web.Response:
        """Remove agent"""
        agent_id = request.match_info["id"]

        if agent_id not in self.agents:
            return web.Response(status=404)

        del self.agents[agent_id]
        return web.Response(status=200)


async def main():
    """Main entry point"""
    try:
        dashboard = DashboardService()
        runner = web.AppRunner(dashboard.app)
        await runner.setup()

        site = web.TCPSite(runner, "localhost", 8080)
        await site.start()

        logger.info("Dashboard service running on http://localhost:8080")

        # Keep the service running
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        logger.error(f"Error in dashboard service: {str(e)}")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
