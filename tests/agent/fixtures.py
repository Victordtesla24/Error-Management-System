"""Test fixtures for agent tests."""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Generator, Tuple
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
def mock_services(test_project_path: Path) -> Tuple[MagicMock, MagicMock, MagicMock]:
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
async def monitor(
    mock_services: Tuple[MagicMock, MagicMock, MagicMock],
    test_project_path: Path,
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[AgentMonitor, None]:
    """Create agent monitor instance with mocked dependencies."""
    memory_manager, metrics_collector, error_service = mock_services

    # Mock the factory to return our mock services
    with patch(
        "src.error_management.factory.ServiceFactory.create_all_services",
        return_value=(memory_manager, metrics_collector, error_service),
    ):
        monitor = AgentMonitor(project_path=test_project_path)
        monitor._loop = event_loop
        yield monitor


@pytest_asyncio.fixture(autouse=True)
async def cleanup_monitor(monitor: AgentMonitor) -> AsyncGenerator[None, None]:
    """Cleanup fixture that runs automatically after each test."""
    yield
    # Cleanup
    for agent_id in list(monitor._agents.keys()):
        monitor.stop_agent(agent_id)
        await asyncio.sleep(0.1)

    # Wait for threads
    for thread in monitor._monitors.values():
        thread.join(timeout=1)
