"""Tests for agent monitoring functionality."""

import asyncio
from datetime import datetime
from typing import Any

import pytest

from src.dashboard.monitoring.agent_monitor import AgentMonitor

from .fixtures import cleanup_monitor, mock_services, monitor, test_project_path


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


@pytest.mark.asyncio
async def test_metrics_collection_frequency(monitor: AgentMonitor) -> None:
    """Test that metrics are collected at the expected frequency."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Get initial timestamp
    initial_time = datetime.now()
    initial_metrics = monitor.get_agent_status(agent_id)["metrics"].copy()

    # Wait for multiple collection cycles
    await asyncio.sleep(0.5)

    # Get final metrics
    final_metrics = monitor.get_agent_status(agent_id)["metrics"]
    final_time = datetime.now()

    # Verify metrics were updated
    assert final_metrics["active_time"] > initial_metrics["active_time"]

    # Calculate collection frequency
    time_diff = (final_time - initial_time).total_seconds()
    updates = final_metrics["active_time"] - initial_metrics["active_time"]
    frequency = updates / time_diff

    # Verify frequency is within expected range (approximately every 0.1 seconds)
    assert 8 <= frequency <= 12  # Allow some variance


@pytest.mark.asyncio
async def test_metrics_buffer_management(monitor: AgentMonitor) -> None:
    """Test that metrics history is properly managed."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Generate many log entries
    for i in range(2000):  # More than buffer size
        monitor._agents[agent_id]["logs"].append(
            {"timestamp": datetime.now(), "level": "INFO", "message": f"Test log {i}"}
        )

    # Verify buffer size is maintained
    logs = monitor.get_agent_logs(agent_id)
    assert len(logs) <= 1000  # Max buffer size

    # Verify most recent logs are kept
    assert "Test log 1999" in logs[-1]["message"]
