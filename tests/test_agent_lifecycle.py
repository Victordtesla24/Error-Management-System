"""Tests for agent lifecycle management."""

import asyncio
from datetime import datetime

import pytest

from src.dashboard.monitoring.agent_monitor import AgentMonitor


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
