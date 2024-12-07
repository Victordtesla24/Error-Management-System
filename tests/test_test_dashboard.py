"""
Tests for the dashboard service and UI components
"""

import asyncio
import shutil
import tempfile
from pathlib import Path

import pytest

from dashboard.service import DashboardService

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def dashboard_app():
    """Create application for testing"""
    dashboard = DashboardService()
    return dashboard.app


@pytest.fixture
async def client(aiohttp_client, dashboard_app):
    """Create test client"""
    return await aiohttp_client(dashboard_app)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_system_status(client):
    """Test system status endpoint"""
    resp = await client.get("/api/system/status")
    assert resp.status == 200
    data = await resp.json()
    assert "projects" in data
    assert "agents" in data
    assert "cpu_usage" in data
    assert "memory_usage" in data


@pytest.mark.asyncio
async def test_project_management(client, temp_project_dir):
    """Test project management endpoints"""
    # Add project
    resp = await client.post("/api/projects", json={"path": temp_project_dir})
    assert resp.status == 200
    data = await resp.json()
    project_id = data["id"]

    # List projects
    resp = await client.get("/api/projects")
    assert resp.status == 200
    projects = await resp.json()
    assert len(projects) == 1
    assert projects[0]["path"] == temp_project_dir

    # Get project status
    status_url = f"/api/projects/{project_id}/status"
    resp = await client.get(status_url)
    assert resp.status == 200
    status = await resp.json()
    assert status["id"] == project_id
    assert status["path"] == temp_project_dir

    # Remove project
    delete_url = f"/api/projects/{project_id}"
    resp = await client.delete(delete_url)
    assert resp.status == 200

    # Verify project removed
    resp = await client.get("/api/projects")
    assert resp.status == 200
    projects = await resp.json()
    assert len(projects) == 0


@pytest.mark.asyncio
async def test_agent_management(client):
    """Test agent management endpoints"""
    # Create agent
    resp = await client.post("/api/agents")
    assert resp.status == 200
    data = await resp.json()
    agent_id = data["id"]

    # List agents
    resp = await client.get("/api/agents")
    assert resp.status == 200
    agents = await resp.json()
    assert len(agents) == 1
    assert agents[0]["id"] == agent_id

    # Get agent status
    status_url = f"/api/agents/{agent_id}/status"
    resp = await client.get(status_url)
    assert resp.status == 200
    status = await resp.json()
    assert status["id"] == agent_id

    # Remove agent
    delete_url = f"/api/agents/{agent_id}"
    resp = await client.delete(delete_url)
    assert resp.status == 200

    # Verify agent removed
    resp = await client.get("/api/agents")
    assert resp.status == 200
    agents = await resp.json()
    assert len(agents) == 0


@pytest.mark.asyncio
async def test_security_metrics(client):
    """Test security metrics endpoint"""
    resp = await client.get("/api/system/security-metrics")
    assert resp.status == 200
    data = await resp.json()
    assert "securityScore" in data
    assert "activeThreats" in data
    assert "certificateStatus" in data


@pytest.mark.asyncio
async def test_system_controls(client):
    """Test system control endpoints"""
    # Start system
    resp = await client.post("/api/system/start")
    assert resp.status == 200

    # Stop system
    resp = await client.post("/api/system/stop")
    assert resp.status == 200

    # Restart system
    resp = await client.post("/api/system/restart")
    assert resp.status == 200


@pytest.mark.asyncio
async def test_concurrent_operations(client, temp_project_dir):
    """Test concurrent operations"""

    # Create multiple projects concurrently
    async def create_project(index):
        project_dir = Path(temp_project_dir) / f"project_{index}"
        project_dir.mkdir()
        resp = await client.post("/api/projects", json={"path": str(project_dir)})
        return resp

    responses = await asyncio.gather(*[create_project(i) for i in range(5)])
    assert all(r.status == 200 for r in responses)

    # Verify all projects created
    resp = await client.get("/api/projects")
    assert resp.status == 200
    projects = await resp.json()
    assert len(projects) == 5


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling"""
    # Invalid project path
    resp = await client.post("/api/projects", json={"path": "/nonexistent/path"})
    assert resp.status == 400

    # Invalid agent ID
    resp = await client.get("/api/agents/invalid-id/status")
    assert resp.status == 404

    # Invalid endpoint
    resp = await client.get("/api/invalid/endpoint")
    assert resp.status == 404


@pytest.mark.asyncio
async def test_metrics_collection(client):
    """Test metrics collection"""
    # Create test data
    await client.post("/api/agents")
    await client.post("/api/agents")

    # Get metrics
    resp = await client.get("/api/system/metrics")
    assert resp.status == 200
    metrics = await resp.json()

    assert metrics["agent_count"] == 2
    assert "error_count" in metrics
    assert "fix_time" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
