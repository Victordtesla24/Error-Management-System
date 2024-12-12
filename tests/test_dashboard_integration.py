"""
Integration tests for Dashboard functionality
"""

import asyncio
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.dashboard.services.dashboard_service import DashboardService
from src.error_management.error_manager import ErrorManager, ErrorModel
from src.error_management.memory_manager import MemoryManager
from src.error_management.metrics import MetricsCollector, SystemMetrics


@pytest.fixture
def error_manager(tmp_path):
    """Create an error manager instance."""
    manager = ErrorManager(project_root=tmp_path)
    # Mock memory manager
    manager._memory_manager.start_monitoring = MagicMock()
    manager._memory_manager.stop_monitoring = MagicMock()
    manager._memory_manager.get_usage_metrics = MagicMock(return_value={})
    return manager


@pytest.fixture
def memory_manager():
    """Create a memory manager instance."""
    manager = MemoryManager()
    manager.start_monitoring = MagicMock()
    manager.stop_monitoring = MagicMock()
    manager.get_usage_metrics = MagicMock(return_value={})
    return manager


@pytest.fixture
def metrics_collector(memory_manager):
    """Create a metrics collector instance."""
    collector = MetricsCollector(memory_manager=memory_manager)
    collector.collect_metrics = MagicMock(
        return_value=SystemMetrics(
            memory_usage=50.0,
            cpu_usage=25.0,
            response_time=0.1,
            error_count=0,
            success_rate=100.0,
        )
    )
    return collector


@pytest.fixture
async def dashboard_service(error_manager, metrics_collector):
    """Create and start a dashboard service instance."""
    service = DashboardService(
        error_manager=error_manager, metrics_collector=metrics_collector
    )
    await service.start()
    try:
        await asyncio.sleep(0.1)  # Allow service to initialize
        return service
    finally:
        await service.stop()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dashboard_error_integration(dashboard_service, error_manager, tmp_path):
    """Test integration between dashboard and error management system."""
    # Get the actual service instance
    service = await dashboard_service

    # Create test error
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    error = ErrorModel(
        id=f"{test_file}:1",
        file_path=test_file,
        line_number=1,
        error_type="Style",
        message="Missing docstring",
    )

    # Add error through error manager
    await error_manager.add_error_async(error)

    # Allow dashboard to update
    await asyncio.sleep(0.1)

    # Verify error appears in dashboard
    dashboard_errors = await service.get_active_errors()
    assert len(dashboard_errors) > 0
    assert any(e["id"] == error.id for e in dashboard_errors)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dashboard_metrics_integration(
    dashboard_service, memory_manager, metrics_collector
):
    """Test integration between dashboard and system metrics."""
    # Get the actual service instance
    service = await dashboard_service

    # Allow dashboard to collect initial metrics
    await asyncio.sleep(0.1)

    # Get metrics from dashboard
    dashboard_metrics = await service.get_system_metrics()

    # Verify metrics are present
    assert "memory_usage" in dashboard_metrics
    assert "cpu_usage" in dashboard_metrics
    assert isinstance(dashboard_metrics["memory_usage"], (int, float))
    assert isinstance(dashboard_metrics["cpu_usage"], (int, float))

    # Verify metrics values match collector
    collector_metrics = metrics_collector.collect_metrics()
    assert dashboard_metrics["memory_usage"] == collector_metrics.memory_usage
    assert dashboard_metrics["cpu_usage"] == collector_metrics.cpu_usage


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dashboard_notification_flow(dashboard_service, error_manager, tmp_path):
    """Test end-to-end notification flow."""
    # Get the actual service instance
    service = await dashboard_service

    # Create and process an error that should trigger a notification
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    error = ErrorModel(
        id=f"{test_file}:1",
        file_path=test_file,
        line_number=1,
        error_type="Critical",
        message="Security vulnerability detected",
    )

    # Add and process error
    await error_manager.add_error_async(error)
    await error_manager.process_error(error.id)

    # Add notification to dashboard
    service.add_notification(
        {
            "error_id": error.id,
            "type": "Critical",
            "message": "Security vulnerability detected",
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Check for notification in dashboard
    notifications = await service.get_notifications()
    assert len(notifications) > 0
    assert any(n["error_id"] == error.id for n in notifications)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dashboard_realtime_updates(dashboard_service, error_manager, tmp_path):
    """Test real-time updates in dashboard."""
    # Get the actual service instance
    service = await dashboard_service

    # Create initial error
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    error1 = ErrorModel(
        id=f"{test_file}:1",
        file_path=test_file,
        line_number=1,
        error_type="Warning",
        message="First warning",
    )

    # Add first error
    await error_manager.add_error_async(error1)

    # Allow dashboard to update
    await asyncio.sleep(0.1)

    # Get initial dashboard state
    initial_errors = await service.get_active_errors()
    initial_count = len(initial_errors)

    # Add second error
    error2 = ErrorModel(
        id=f"{test_file}:2",
        file_path=test_file,
        line_number=2,
        error_type="Warning",
        message="Second warning",
    )
    await error_manager.add_error_async(error2)

    # Allow dashboard to update
    await asyncio.sleep(0.1)

    # Verify dashboard updates
    updated_errors = await service.get_active_errors()
    assert len(updated_errors) == initial_count + 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metrics_history(dashboard_service, metrics_collector):
    """Test metrics history tracking."""
    # Get the actual service instance
    service = await dashboard_service

    # Allow dashboard to collect multiple metrics samples
    for _ in range(3):
        await asyncio.sleep(0.1)

    # Get metrics from dashboard
    metrics = await service.get_system_metrics()

    # Verify metrics are present and valid
    assert metrics["memory_usage"] == 50.0  # From mock
    assert metrics["cpu_usage"] == 25.0  # From mock
    assert metrics["success_rate"] == 100.0  # From mock


if __name__ == "__main__":
    pytest.main(["-v", "--integration", __file__])
