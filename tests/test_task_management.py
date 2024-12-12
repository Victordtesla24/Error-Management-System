"""Tests for agent task management functionality."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator

import pytest
import pytest_asyncio

from src.dashboard.monitoring.agent_monitor import AgentMonitor

from .fixtures import cleanup_monitor, mock_services, monitor, test_project_path


def create_test_task(task_type: str = "Run Tests") -> Dict[str, Any]:
    """Create a test task configuration."""
    return {
        "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": task_type,
        "project_path": "/test/path",
        "priority": "Medium",
        "timeout": 30,
        "status": "pending",
        "created_at": datetime.now(),
        "config": {
            "test_types": ["Unit Tests"],
            "test_pattern": "test_*.py",
            "parallel": True,
        },
    }


@pytest.mark.asyncio
async def test_task_assignment(monitor: AgentMonitor) -> None:
    """Test assigning a task to an agent."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create and assign task
    task = create_test_task()
    success = monitor.assign_task(agent_id, task)

    assert success is True

    # Verify task was added
    agent_status = monitor.get_agent_status(agent_id)
    assert agent_status is not None
    assert "tasks" in agent_status
    assert len(agent_status["tasks"]) == 1
    assert agent_status["tasks"][0]["id"] == task["id"]


@pytest.mark.asyncio
async def test_task_execution(monitor: AgentMonitor) -> None:
    """Test task execution flow."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create and assign task
    task = create_test_task()
    monitor.assign_task(agent_id, task)

    # Wait for execution
    await asyncio.sleep(0.5)

    # Get task status
    task_status = monitor.get_task_status(agent_id, task["id"])
    assert task_status is not None
    assert task_status["status"] in ["completed", "running", "failed"]

    if task_status["status"] == "completed":
        assert "completed_at" in task_status
        assert "duration" in task_status
        assert "results" in task_status


@pytest.mark.asyncio
async def test_multiple_task_handling(monitor: AgentMonitor) -> None:
    """Test handling multiple tasks for an agent."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create and assign multiple tasks
    tasks = [
        create_test_task("Run Tests"),
        create_test_task("Code Analysis"),
        create_test_task("Security Scan"),
    ]

    for task in tasks:
        success = monitor.assign_task(agent_id, task)
        assert success is True

    # Wait for processing
    await asyncio.sleep(0.5)

    # Verify tasks are tracked
    agent_status = monitor.get_agent_status(agent_id)
    assert agent_status is not None
    assert len(agent_status["tasks"]) == len(tasks)

    # Verify task order
    task_ids = [t["id"] for t in agent_status["tasks"]]
    assert task_ids == [
        t["id"] for t in tasks
    ]  # Tasks should be in order of assignment


@pytest.mark.asyncio
async def test_task_priority_handling(monitor: AgentMonitor) -> None:
    """Test task priority handling."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create tasks with different priorities
    tasks = [
        {**create_test_task(), "priority": "Low"},
        {**create_test_task(), "priority": "High"},
        {**create_test_task(), "priority": "Medium"},
    ]

    for task in tasks:
        monitor.assign_task(agent_id, task)

    # Wait for processing
    await asyncio.sleep(0.5)

    # Verify high priority task is processed first
    agent_status = monitor.get_agent_status(agent_id)
    assert agent_status is not None
    running_tasks = [t for t in agent_status["tasks"] if t["status"] == "running"]
    if running_tasks:
        assert running_tasks[0]["priority"] == "High"


@pytest.mark.asyncio
async def test_task_timeout(monitor: AgentMonitor) -> None:
    """Test task timeout handling."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create task with short timeout
    task = {**create_test_task(), "timeout": 1}  # 1 minute timeout
    monitor.assign_task(agent_id, task)

    # Wait for timeout
    await asyncio.sleep(1.5)  # Wait longer than timeout

    # Verify task status
    task_status = monitor.get_task_status(agent_id, task["id"])
    assert task_status is not None
    assert task_status["status"] == "failed"
    assert "timeout" in task_status.get("error", "").lower()


@pytest.mark.asyncio
async def test_task_error_handling(monitor: AgentMonitor) -> None:
    """Test error handling during task execution."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create task that will fail
    task = {
        **create_test_task(),
        "type": "Custom Task",
        "config": {"command": "invalid_command", "args": []},
    }

    monitor.assign_task(agent_id, task)

    # Wait for execution
    await asyncio.sleep(0.5)

    # Verify error handling
    task_status = monitor.get_task_status(agent_id, task["id"])
    assert task_status is not None
    assert task_status["status"] == "failed"
    assert "error" in task_status
    assert task_status["error"] is not None

    # Verify error is logged
    agent_logs = monitor.get_agent_logs(agent_id)
    error_logs = [log for log in agent_logs if log["level"] == "ERROR"]
    assert len(error_logs) > 0


@pytest.mark.asyncio
async def test_task_progress_tracking(monitor: AgentMonitor) -> None:
    """Test task progress tracking."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create task
    task = create_test_task("Run Tests")
    monitor.assign_task(agent_id, task)

    # Wait for execution to start
    await asyncio.sleep(0.2)

    # Get task status
    task_status = monitor.get_task_status(agent_id, task["id"])
    assert task_status is not None

    if task_status["status"] == "running":
        assert "progress" in task_status
        assert isinstance(task_status["progress"], (int, float))
        assert 0 <= task_status["progress"] <= 1


@pytest.mark.asyncio
async def test_task_results_handling(monitor: AgentMonitor) -> None:
    """Test handling of task results."""
    agent_id = "test_agent_1"
    monitor.start_agent(agent_id)
    await asyncio.sleep(0.1)  # Wait for start

    # Create and assign task
    task = create_test_task("Code Analysis")
    monitor.assign_task(agent_id, task)

    # Wait for completion
    await asyncio.sleep(1.0)

    # Get task status
    task_status = monitor.get_task_status(agent_id, task["id"])
    assert task_status is not None

    if task_status["status"] == "completed":
        assert "results" in task_status
        results = task_status["results"]
        assert isinstance(results, dict)

        # Verify results structure
        if task["type"] == "Code Analysis":
            assert "code_quality" in results or "complexity" in results

        # Verify metrics update
        agent_metrics = monitor.get_agent_status(agent_id)
        assert agent_metrics is not None
        assert agent_metrics["metrics"]["tasks_completed"] > 0
