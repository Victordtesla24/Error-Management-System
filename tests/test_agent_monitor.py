"""Tests for agent monitoring functionality."""

import asyncio
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from src.dashboard.monitoring.agent_monitor import AgentMonitor
from src.error_management.factory import ServiceFactory
from src.error_management.memory_manager import MemoryManager
from src.error_management.metrics import MetricsCollector, SystemMetrics
from src.error_management.service import ErrorManagementService


@pytest.fixture
def test_project_path(tmp_path: Path) -> Path:
    """Create a temporary project path for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir


@pytest.fixture
def mock_services(test_project_path: Path):
    """Create mock services."""
    memory_manager = MagicMock(spec=MemoryManager)
    memory_manager.get_usage_metrics.return_value = {}
    memory_manager.start_monitoring.return_value = None
    memory_manager.stop_monitoring.return_value = None

    metrics_collector = MagicMock(spec=MetricsCollector)
    # Return initial metrics of 0, then update to 10.0 after delay
    metrics_collector.collect_metrics.side_effect = [
        SystemMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            response_time=0.1,
            success_rate=100.0,
            error_count=0,
        ),
        SystemMetrics(
            cpu_usage=10.0,
            memory_usage=20.0,
            response_time=0.1,
            success_rate=100.0,
            error_count=0,
        ),
    ]

    error_service = MagicMock(spec=ErrorManagementService)

    # Mock async methods
    async def mock_start() -> None:
        pass

    async def mock_stop() -> None:
        pass

    async def mock_get_errors() -> list:
        return []

    async def mock_scan_security() -> MagicMock:
        mock = MagicMock()
        mock.score = 100
        mock.vulnerabilities = 0
        return mock

    async def mock_get_logs() -> list:
        return []

    async def mock_get_activities() -> list:
        return []

    error_service.start = mock_start
    error_service.stop = mock_stop
    error_service.get_errors = mock_get_errors
    error_service.scan_security = mock_scan_security
    error_service.get_logs = mock_get_logs
    error_service.get_activities = mock_get_activities

    return memory_manager, metrics_collector, error_service


@pytest_asyncio.fixture
async def monitor(mock_services, test_project_path: Path, event_loop) -> AgentMonitor:
    """Create agent monitor instance with mocked dependencies."""
    memory_manager, metrics_collector, error_service = mock_services

    # Mock the factory to return our mock services
    with patch.object(
        ServiceFactory,
        "create_all_services",
        return_value=(memory_manager, metrics_collector, error_service),
    ):
        monitor = AgentMonitor(project_path=test_project_path)
        monitor._loop = event_loop
        return monitor


@pytest_asyncio.fixture(autouse=True)
async def cleanup_monitor(monitor: AgentMonitor):
    """Cleanup fixture that runs automatically after each test."""
    yield
    # Cleanup
    for agent_id in list(monitor._agents.keys()):
        monitor.stop_agent(agent_id)
        await asyncio.sleep(0.1)

    # Wait for threads
    for thread in monitor._monitors.values():
        thread.join(timeout=1)


@pytest.mark.asyncio
async def test_start_agent(monitor: AgentMonitor) -> None:
    """Test starting an agent."""
    agent_id = "test_agent_1"
    success = monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for async operations

    assert success is True
    assert agent_id in monitor._agents
    assert monitor._agents[agent_id]["status"] == "running"

    # Verify metrics initialization
    agent_metrics = monitor._agents[agent_id]["metrics"]
    assert agent_metrics["cpu_usage"] == 0.0  # Initial metrics should be 0
    assert agent_metrics["memory_usage"] == 0.0
    assert agent_metrics["success_rate"] == 100.0

    # Verify security initialization
    security = monitor._agents[agent_id]["security"]
    assert security["score"] == 100
    assert security["vulnerabilities"] == 0
    assert isinstance(security["last_scan"], datetime)

    # Verify monitoring thread
    assert agent_id in monitor._monitors
    assert monitor._monitors[agent_id].is_alive()


@pytest.mark.asyncio
async def test_stop_agent(monitor: AgentMonitor) -> None:
    """Test stopping an agent."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start to complete

    success = monitor.stop_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for stop to complete

    assert success is True
    assert monitor._agents[agent_id]["status"] == "stopped"
    assert agent_id not in monitor._monitors


@pytest.mark.asyncio
async def test_agent_metrics_update(monitor: AgentMonitor) -> None:
    """Test that agent metrics are updated over time."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Get initial metrics
    initial_metrics = monitor.get_agent_status(agent_id)["metrics"].copy()
    assert initial_metrics["cpu_usage"] == 0.0  # Initial metrics should be 0
    assert initial_metrics["memory_usage"] == 0.0

    # Wait for updates
    await asyncio.sleep(0.5)

    # Get updated metrics
    updated_metrics = monitor.get_agent_status(agent_id)["metrics"]

    # Verify metrics changed
    assert updated_metrics["cpu_usage"] == 10.0  # Updated metrics should be 10.0
    assert updated_metrics["memory_usage"] == 20.0
    assert updated_metrics["success_rate"] == 100.0
    assert updated_metrics["active_time"] > initial_metrics["active_time"]


@pytest.mark.asyncio
async def test_agent_logs_generation(monitor: AgentMonitor) -> None:
    """Test agent log generation."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Wait for logs
    await asyncio.sleep(0.5)

    logs = monitor.get_agent_logs(agent_id)
    assert isinstance(logs, list)

    # Add test log
    monitor._agents[agent_id]["logs"].append(
        {"timestamp": datetime.now(), "level": "INFO", "message": "Test log"}
    )

    updated_logs = monitor.get_agent_logs(agent_id)
    assert len(updated_logs) > 0
    assert updated_logs[-1]["message"] == "Test log"


@pytest.mark.asyncio
async def test_agent_activities_tracking(monitor: AgentMonitor) -> None:
    """Test agent activity tracking."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Get initial activities (should have Agent Start activity)
    initial_activities = monitor.get_agent_activities(agent_id)
    assert isinstance(initial_activities, list)
    assert len(initial_activities) > 0
    assert initial_activities[0]["type"] == "Agent Start"

    # Add test activity
    test_activity = {
        "timestamp": datetime.now(),
        "type": "Test",
        "status": "Success",
        "details": "Test activity",
    }
    monitor._agents[agent_id]["activities"].insert(0, test_activity)

    # Get updated activities
    updated_activities = monitor.get_agent_activities(agent_id)
    assert len(updated_activities) > len(initial_activities)
    assert (
        updated_activities[0]["type"] == "Test"
    )  # Most recent activity should be Test


@pytest.mark.asyncio
async def test_security_monitoring(monitor: AgentMonitor) -> None:
    """Test security metrics monitoring."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Wait for security scan
    await asyncio.sleep(0.5)

    security = monitor.get_agent_security(agent_id)
    assert isinstance(security, dict)
    assert security["score"] == 100
    assert security["vulnerabilities"] == 0
    assert isinstance(security["last_scan"], datetime)


@pytest.mark.asyncio
async def test_container_monitoring(monitor: AgentMonitor) -> None:
    """Test container metrics monitoring."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    container = monitor.get_agent_container(agent_id)
    assert isinstance(container, dict)
    assert container["status"] == "running"
    assert container["image"] == "error-management-agent:latest"
    assert "ports" in container
    assert "volumes" in container
    assert "resources" in container


@pytest.mark.asyncio
async def test_concurrent_agents(monitor: AgentMonitor) -> None:
    """Test monitoring multiple agents concurrently."""
    agent_ids = [f"test_agent_{i}" for i in range(3)]

    # Start multiple agents
    for agent_id in agent_ids:
        success = monitor.start_agent(agent_id)
        assert success is True
        await asyncio.sleep(0.1)  # Wait for each start

    # Wait for updates
    await asyncio.sleep(0.5)

    # Verify all agents are monitored
    for agent_id in agent_ids:
        status = monitor.get_agent_status(agent_id)
        assert status is not None
        assert status["status"] == "running"
        assert status["metrics"]["cpu_usage"] == 10.0  # Updated metrics
        assert status["metrics"]["memory_usage"] == 20.0
        assert status["metrics"]["success_rate"] == 100.0


@pytest.mark.asyncio
async def test_agent_cleanup(monitor: AgentMonitor) -> None:
    """Test proper cleanup of agent resources."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Get monitor thread
    thread = monitor._monitors[agent_id]
    assert thread.is_alive()

    # Stop agent
    monitor.stop_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for stop

    # Verify thread stopped
    thread.join(timeout=1)
    assert not thread.is_alive()
    assert agent_id not in monitor._monitors


@pytest.mark.asyncio
async def test_monitor_thread_safety(monitor: AgentMonitor) -> None:
    """Test thread safety of monitoring operations."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    async def update_metrics() -> None:
        for _ in range(5):
            status = monitor.get_agent_status(agent_id)
            if status:
                metrics = status["metrics"]
                assert metrics["cpu_usage"] == 10.0  # Updated metrics
                assert metrics["memory_usage"] == 20.0
            await asyncio.sleep(0.1)

    # Create multiple tasks accessing metrics
    tasks = [asyncio.create_task(update_metrics()) for _ in range(3)]

    # Wait for tasks to complete
    await asyncio.gather(*tasks)

    # Verify agent still functioning
    assert monitor.get_agent_status(agent_id)["status"] == "running"
