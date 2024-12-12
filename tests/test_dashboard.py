"""
Tests for the Dashboard Service
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.dashboard.service import DashboardService

logger = logging.getLogger(__name__)


@pytest.fixture
async def service():
    """Create a test service instance"""
    service = None
    try:
        async with asyncio.timeout(5.0):
            service = await DashboardService.create()
            yield service
    finally:
        if service:
            await service.stop()
            await service.stop_background_tasks()


@pytest.mark.asyncio
async def test_dashboard_initialization():
    """Test dashboard initialization."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            status = await service.get_system_status()
            assert status["status"] == "operational"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_metrics():
    """Test dashboard metrics."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            metrics = await service.get_metrics()
            assert isinstance(metrics, dict)
            assert "cpu_usage" in metrics
            assert "memory_usage" in metrics
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_notifications():
    """Test dashboard notifications."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            await service.add_notification("Test notification", level="info")
            notifications = await service.get_notifications()
            assert len(notifications) > 0
            assert notifications[0]["message"] == "Test notification"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_background_tasks():
    """Test dashboard background tasks."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            await service.start_background_tasks()
            status = await service.get_system_status()
            assert status["status"] == "operational"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_agent_management():
    """Test dashboard agent management."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            agent = await service.create_agent("Test Agent", "Error Fixer", ["Python"])
            assert agent["name"] == "Test Agent"
            assert agent["type"] == "Error Fixer"
            assert agent["role"] == "Error Fixer"  # Both type and role should be set
            assert agent["status"] == "active"

            # Verify agent info
            agent_info = await service.get_agent_info(agent["id"])
            assert agent_info is not None
            assert agent_info["name"] == "Test Agent"
            assert agent_info["type"] == "Error Fixer"
            assert agent_info["status"] == "active"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_project_management():
    """Test dashboard project management."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            project = await service.create_project("Test Project", "/test/path", {})
            assert project["name"] == "Test Project"
            assert project["path"] == "/test/path"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_error_handling():
    """Test dashboard error handling."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            with pytest.raises(ValueError):
                await service.create_project("", "", {})
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_system_status():
    """Test dashboard system status."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            await service.create_agent("Test Agent", "Error Fixer", ["Python"])
            await service.create_project("Test Project", os.getcwd(), {})
            status = await service.get_system_status()
            assert status["active_agents"] == 1
            assert status["active_projects"] == 1
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_cleanup():
    """Test dashboard cleanup."""
    service = DashboardService()
    try:
        async with asyncio.timeout(5.0):
            await service.start()
            status = await service.get_system_status()
            assert status["status"] == "operational"
            await service.stop()
            status = await service.get_system_status()
            assert status["status"] == "stopped"
    finally:
        await service.stop()


@pytest.mark.asyncio
async def test_dashboard_agent_monitoring():
    """Test dashboard agent monitoring."""
    service = None
    try:
        # Create service
        service = await DashboardService.create()
        assert service is not None, "Failed to create service"

        # Create test agent
        agent = await service.create_agent(
            "Test Agent",
            "Monitor",
            ["Python"],
            scan_interval=0.1,
            monitoring_interval=0.1,
        )
        assert agent is not None, "Failed to create agent"
        assert agent["id"] is not None, "Agent ID is missing"

        # Initial status should be active
        agent_info = await service.get_agent_info(agent["id"])
        assert agent_info is not None, "Failed to get agent info"
        assert agent_info["status"] == "active", "Initial agent status should be active"

        # Start background tasks with shorter intervals
        await service.start_background_tasks(monitoring_interval=0.1)

        # Wait for monitoring to start
        await asyncio.sleep(0.2)

        # Monitor agents with timeout
        try:
            async with asyncio.timeout(2.0):  # Increased timeout
                monitoring_result = await service.monitor_agents()
                assert monitoring_result is not None, "Failed to get monitoring result"
                assert (
                    monitoring_result["status"] == "ok"
                ), f"Unexpected status: {monitoring_result.get('status')}"
                assert (
                    monitoring_result["active_agents"] == 1
                ), f"Expected 1 active agent, got {monitoring_result.get('active_agents')}"
                assert (
                    monitoring_result["inactive_agents"] == 0
                ), f"Expected 0 inactive agents, got {monitoring_result.get('inactive_agents')}"
        except asyncio.TimeoutError:
            raise AssertionError("Timed out waiting for initial monitoring result")

        # Simulate agent inactivity by modifying heartbeat
        async with service._lock:
            service.agents[agent["id"]]["last_heartbeat"] = (
                datetime.now().replace(year=2000).isoformat()
            )

        # Wait for monitoring to update
        await asyncio.sleep(0.2)

        # Monitor again - should detect inactive agent with timeout
        try:
            async with asyncio.timeout(2.0):  # Increased timeout
                monitoring_result = await service.monitor_agents()
                assert (
                    monitoring_result is not None
                ), "Failed to get monitoring result after inactivity"
                assert (
                    monitoring_result["status"] == "warning"
                ), f"Expected warning status, got {monitoring_result.get('status')}"
                assert (
                    monitoring_result["active_agents"] == 0
                ), f"Expected 0 active agents, got {monitoring_result.get('active_agents')}"
                assert (
                    monitoring_result["inactive_agents"] == 1
                ), f"Expected 1 inactive agent, got {monitoring_result.get('inactive_agents')}"
        except asyncio.TimeoutError:
            raise AssertionError(
                "Timed out waiting for monitoring result after inactivity"
            )

        # Verify agent status update
        agent_info = await service.get_agent_info(agent["id"])
        assert agent_info is not None, "Failed to get agent info after inactivity"
        assert (
            agent_info["status"] == "inactive"
        ), f"Expected inactive status, got {agent_info.get('status')}"

    except Exception as e:
        logger.error(f"Error in agent monitoring test: {str(e)}")
        raise
    finally:
        if service:
            try:
                async with asyncio.timeout(1.0):
                    await service.stop()
            except asyncio.TimeoutError:
                logger.warning("Timeout stopping service in agent monitoring test")
            except Exception as e:
                logger.error(
                    f"Error stopping service in agent monitoring test: {str(e)}"
                )
                raise


@pytest.mark.asyncio
async def test_dashboard_project_scanning():
    """Test dashboard project scanning."""
    service = DashboardService()
    try:
        await service.start()
        project = await service.create_project("Test Project", os.getcwd(), {})
        errors = await service._scan_project_for_errors(project["id"])
        assert isinstance(errors, list)  # There might be no errors
    except Exception as e:
        logger.error(f"Error in project scanning test: {e}")
        raise
    finally:
        try:
            await service.stop()
        except Exception as e:
            logger.error(f"Error stopping service in project scanning test: {e}")


@pytest.mark.asyncio
async def test_dashboard_metrics_update():
    """Test dashboard metrics update."""
    service = DashboardService()
    try:
        await service.start()
        await asyncio.sleep(0.2)  # Wait for metrics to update
        metrics = await service.get_metrics()
        assert metrics.get("cpu_usage") is not None
        assert metrics.get("memory_usage") is not None
    except Exception as e:
        logger.error(f"Error in metrics update test: {e}")
        raise
    finally:
        try:
            await service.stop()
        except Exception as e:
            logger.error(f"Error stopping service in metrics update test: {e}")
