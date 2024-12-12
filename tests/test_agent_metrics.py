"""Tests for agent metrics and monitoring."""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import streamlit as st

from src.dashboard.metrics.agent_metrics import AgentMetricsCollector
from src.error_management.memory_manager import MemoryManager
from src.error_management.metrics import MetricsCollector, SystemMetrics
from src.error_management.service import ErrorManagementService


class MockSessionState:
    """Mock Streamlit session state."""

    def __init__(self):
        self._data = {
            "agents": [
                {
                    "id": "test_agent_1",
                    "name": "Test Agent",
                    "type": "Error Detection",
                    "status": "running",
                }
            ],
            "agent_logs": {"test_agent_1": []},
            "agent_metrics": {
                "test_agent_1": {
                    "errors_fixed": 0,
                    "success_rate": 100,
                    "avg_response_time": 0,
                    "active_time": 0,
                }
            },
            "agent_activities": {"test_agent_1": []},
            "agent_security": {
                "test_agent_1": {
                    "permissions": ["read", "write", "execute"],
                    "vulnerabilities_detected": 0,
                    "security_score": 100,
                    "last_security_scan": datetime.now(),
                }
            },
        }

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __contains__(self, key):
        return key in self._data


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit session state."""
    mock_state = MockSessionState()
    monkeypatch.setattr(st, "session_state", mock_state)
    return mock_state


@pytest.fixture
def test_project_path(tmp_path: Path) -> Path:
    """Create a temporary project path for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir


@pytest.fixture
def metrics_collector(mock_session_state, test_project_path: Path):
    """Create metrics collector instance."""
    memory_manager = MemoryManager()
    error_service = ErrorManagementService(project_path=test_project_path)

    # Mock async methods
    async def mock_get_errors():
        return []

    async def mock_scan_security():
        mock = MagicMock()
        mock.score = 100
        mock.vulnerabilities = 0
        return mock

    async def mock_get_logs():
        return []

    async def mock_get_activities():
        return []

    error_service.get_errors_async = mock_get_errors
    error_service.scan_security_async = mock_scan_security
    error_service.get_logs_async = mock_get_logs
    error_service.get_activities_async = mock_get_activities

    return AgentMetricsCollector(memory_manager, error_service)


@pytest.mark.asyncio
async def test_update_agent_metrics(metrics_collector, mock_session_state):
    """Test agent metrics update."""
    agent_id = "test_agent_1"
    initial_metrics = st.session_state.agent_metrics[agent_id].copy()

    updated_metrics = metrics_collector.update_agent_metrics(agent_id)

    assert isinstance(updated_metrics, dict)
    assert "cpu_usage" in updated_metrics
    assert "memory_usage" in updated_metrics
    assert "response_time" in updated_metrics
    assert "success_rate" in updated_metrics
    assert updated_metrics["active_time"] > initial_metrics["active_time"]


@pytest.mark.asyncio
async def test_log_agent_activity(metrics_collector, mock_session_state):
    """Test agent activity logging."""
    agent_id = "test_agent_1"
    activity_type = "Test Activity"
    status = "Success"
    details = "Test activity details"
    project = "/test/project"

    metrics_collector.log_agent_activity(
        agent_id, activity_type, status, details, project
    )

    activities = st.session_state.agent_activities[agent_id]
    assert len(activities) > 0
    latest_activity = activities[0]
    assert latest_activity["type"] == activity_type
    assert latest_activity["status"] == status
    assert latest_activity["details"] == details
    assert latest_activity["project"] == project
    assert isinstance(latest_activity["timestamp"], datetime)


@pytest.mark.asyncio
async def test_get_agent_metrics(metrics_collector, mock_session_state):
    """Test getting agent metrics."""
    agent_id = "test_agent_1"
    metrics = metrics_collector.get_agent_metrics(agent_id)

    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "response_time" in metrics
    assert "success_rate" in metrics


@pytest.mark.asyncio
async def test_get_agent_security(metrics_collector, mock_session_state):
    """Test getting agent security metrics."""
    agent_id = "test_agent_1"
    security = metrics_collector.get_agent_security(agent_id)

    assert isinstance(security, dict)
    assert "permissions" in security
    assert "security_score" in security
    assert isinstance(security["permissions"], list)


@pytest.mark.asyncio
async def test_get_agent_logs(metrics_collector, mock_session_state):
    """Test getting agent logs."""
    agent_id = "test_agent_1"
    # Add some test logs
    st.session_state.agent_logs[agent_id] = [
        {"timestamp": datetime.now(), "level": "INFO", "message": "Test log message"}
    ]

    logs = metrics_collector.get_agent_logs(agent_id)
    assert isinstance(logs, list)
    assert len(logs) > 0
    assert "timestamp" in logs[0]
    assert "level" in logs[0]
    assert "message" in logs[0]


@pytest.mark.asyncio
async def test_get_agent_activities(metrics_collector, mock_session_state):
    """Test getting agent activities."""
    agent_id = "test_agent_1"
    # Add some test activities
    st.session_state.agent_activities[agent_id] = [
        {
            "timestamp": datetime.now(),
            "type": "Test Activity",
            "status": "Success",
            "details": "Test details",
        }
    ]

    activities = metrics_collector.get_agent_activities(agent_id)
    assert isinstance(activities, list)
    assert len(activities) > 0
    assert "timestamp" in activities[0]
    assert "type" in activities[0]
    assert "status" in activities[0]
    assert "details" in activities[0]


@pytest.mark.asyncio
async def test_get_performance_metrics(metrics_collector):
    """Test getting performance metrics."""
    metrics = metrics_collector.get_performance_metrics()

    assert isinstance(metrics, dict)
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "network" in metrics
    assert "response_time" in metrics
    assert "success_rate" in metrics
