"""
Tests for the file monitoring component
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

import psutil
import pytest
from watchdog.events import FileCreatedEvent, FileModifiedEvent

from error_management.error_manager import ErrorManager
from error_management.file_monitor import FileMonitor, SecureFileHandler
from error_management.secure_environment import SecureEnvironment


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def secure_env(temp_project_dir):
    """Create a secure environment instance"""
    return SecureEnvironment(temp_project_dir)


@pytest.fixture
def error_manager(secure_env):
    """Create an error manager instance"""
    return ErrorManager(secure_env)


@pytest.fixture
def file_monitor(secure_env, error_manager):
    """Create a file monitor instance"""
    return FileMonitor(secure_env, error_manager)


@pytest.mark.asyncio
async def test_file_monitor_initialization(file_monitor):
    """Test file monitor initialization"""
    assert file_monitor.secure_env is not None
    assert file_monitor.error_manager is not None
    assert file_monitor.observer is None
    assert file_monitor._running is False


@pytest.mark.asyncio
async def test_start_stop_monitoring(file_monitor):
    """Test starting and stopping file monitoring"""
    # Start monitoring
    monitor_task = asyncio.create_task(file_monitor.start_monitoring())

    # Wait briefly for monitoring to start
    await asyncio.sleep(0.1)
    assert file_monitor._running is True
    assert file_monitor.observer is not None
    assert file_monitor.observer.is_alive()

    # Stop monitoring
    await file_monitor.stop_monitoring()
    assert file_monitor._running is False
    assert not file_monitor.observer.is_alive()

    # Cancel the monitoring task
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_file_handler_security(secure_env, error_manager, temp_project_dir):
    """Test file handler security checks"""
    handler = SecureFileHandler(secure_env, error_manager)

    # Create a file inside project directory
    inside_file = Path(temp_project_dir) / "test.py"
    inside_file.touch()

    # Create a file outside project directory
    outside_file = Path(tempfile.gettempdir()) / "outside.py"
    outside_file.touch()

    try:
        # Test file modification inside project
        event = FileModifiedEvent(str(inside_file))
        handler.on_modified(event)
        await asyncio.sleep(0.1)  # Allow event processing

        # Test file modification outside project
        event = FileModifiedEvent(str(outside_file))
        handler.on_modified(event)
        await asyncio.sleep(0.1)  # Allow event processing

    finally:
        # Cleanup
        if outside_file.exists():
            outside_file.unlink()


@pytest.mark.asyncio
async def test_file_creation_handling(secure_env, error_manager, temp_project_dir):
    """Test handling of file creation events"""
    handler = SecureFileHandler(secure_env, error_manager)

    # Create a new file
    new_file = Path(temp_project_dir) / "new_file.py"
    event = FileCreatedEvent(str(new_file))

    # Simulate file creation event
    new_file.touch()
    handler.on_created(event)

    # Wait for event processing
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_file_modification_handling(secure_env, error_manager, temp_project_dir):
    """Test handling of file modification events"""
    handler = SecureFileHandler(secure_env, error_manager)

    # Create and modify a file
    test_file = Path(temp_project_dir) / "test.py"
    test_file.write_text("initial content")

    event = FileModifiedEvent(str(test_file))

    # Simulate file modification
    test_file.write_text("modified content")
    handler.on_modified(event)

    # Wait for event processing
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_concurrent_file_events(file_monitor, temp_project_dir):
    """Test handling of concurrent file events"""
    # Start monitoring
    monitor_task = asyncio.create_task(file_monitor.start_monitoring())
    await asyncio.sleep(0.1)  # Allow monitoring to start

    try:
        # Create multiple files concurrently
        files = []
        for i in range(5):
            file_path = Path(temp_project_dir) / f"test{i}.py"
            file_path.touch()
            files.append(file_path)

        # Wait for event processing
        await asyncio.sleep(0.5)

        # Modify files concurrently
        for file_path in files:
            file_path.write_text("modified content")

        # Wait for event processing
        await asyncio.sleep(0.5)

    finally:
        # Stop monitoring
        await file_monitor.stop_monitoring()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_file_type_filtering(secure_env, error_manager, temp_project_dir):
    """Test filtering of file types"""
    handler = SecureFileHandler(secure_env, error_manager)

    # Create files of different types
    py_file = Path(temp_project_dir) / "test.py"
    py_file.touch()

    txt_file = Path(temp_project_dir) / "test.txt"
    txt_file.touch()

    # Test Python file event
    py_event = FileModifiedEvent(str(py_file))
    handler.on_modified(py_event)

    # Test text file event
    txt_event = FileModifiedEvent(str(txt_file))
    handler.on_modified(txt_event)

    # Wait for event processing
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_monitoring_resource_usage(file_monitor, temp_project_dir):
    """Test resource usage during monitoring"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Start monitoring
    monitor_task = asyncio.create_task(file_monitor.start_monitoring())
    await asyncio.sleep(0.1)

    try:
        # Create and modify files
        for i in range(100):
            file_path = Path(temp_project_dir) / f"test{i}.py"
            file_path.touch()
            file_path.write_text(f"content {i}")
            await asyncio.sleep(0.01)

        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Ensure memory usage increase is reasonable
        max_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_increase

    finally:
        # Stop monitoring
        await file_monitor.stop_monitoring()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
