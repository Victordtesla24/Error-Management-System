"""
Tests for the main entry point module
"""

import asyncio
import signal
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from error_management.__main__ import ErrorManagementSystem, validate_arguments


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return str(project_dir)


@pytest.fixture
def error_system(temp_project_dir):
    """Create an error management system instance"""
    return ErrorManagementSystem(temp_project_dir)


@pytest.mark.asyncio
async def test_system_initialization(error_system):
    """Test system initialization"""
    assert error_system.project_path is not None
    assert error_system.secure_env is None
    assert error_system.error_manager is None
    assert error_system.file_monitor is None
    assert not error_system._shutdown_event.is_set()


@pytest.mark.asyncio
async def test_system_initialize(error_system):
    """Test system component initialization"""
    await error_system.initialize()
    assert error_system.secure_env is not None
    assert error_system.error_manager is not None
    assert error_system.file_monitor is not None


@pytest.mark.asyncio
async def test_system_signal_handler(error_system):
    """Test system signal handling"""
    # Simulate SIGTERM
    error_system._signal_handler(signal.SIGTERM, None)
    assert error_system._shutdown_event.is_set()


@pytest.mark.asyncio
async def test_system_start_stop(error_system):
    """Test system startup and shutdown"""
    # Mock component methods
    with patch('error_management.__main__.FileMonitor') as mock_monitor, \
         patch('error_management.__main__.ErrorManager') as mock_manager:
        
        # Setup mocks
        mock_monitor_inst = AsyncMock()
        mock_manager_inst = AsyncMock()
        mock_monitor.return_value = mock_monitor_inst
        mock_manager.return_value = mock_manager_inst

        # Start system
        start_task = asyncio.create_task(error_system.start())
        
        # Wait briefly for system to start
        await asyncio.sleep(0.1)
        
        # Trigger shutdown
        error_system._shutdown_event.set()
        
        # Wait for system to stop
        await start_task

        # Verify component lifecycle
        assert mock_monitor_inst.start_monitoring.called
        assert mock_monitor_inst.stop_monitoring.called
        assert mock_manager_inst.start_monitoring.called
        assert mock_manager_inst.stop_monitoring.called


@pytest.mark.asyncio
async def test_system_shutdown(error_system):
    """Test system shutdown"""
    # Initialize components
    await error_system.initialize()
    
    # Mock component methods
    error_system.file_monitor.stop_monitoring = AsyncMock()
    error_system.error_manager.stop_monitoring = AsyncMock()
    
    # Perform shutdown
    await error_system.shutdown()
    
    # Verify components were stopped
    assert error_system.file_monitor.stop_monitoring.called
    assert error_system.error_manager.stop_monitoring.called


def test_validate_arguments_valid(temp_project_dir):
    """Test argument validation with valid path"""
    with patch('sys.argv', ['script.py', temp_project_dir]):
        result = validate_arguments()
        assert result == str(Path(temp_project_dir))


def test_validate_arguments_invalid():
    """Test argument validation with invalid path"""
    with patch('sys.argv', ['script.py', '/nonexistent/path']):
        with pytest.raises(SystemExit):
            validate_arguments()


def test_validate_arguments_missing():
    """Test argument validation with missing path"""
    with patch('sys.argv', ['script.py']):
        with pytest.raises(SystemExit):
            validate_arguments()


@pytest.mark.asyncio
async def test_error_handling(error_system):
    """Test error handling during system operation"""
    # Mock components
    with patch('error_management.__main__.FileMonitor') as mock_monitor, \
         patch('error_management.__main__.ErrorManager') as mock_manager:
        
        # Setup mocks
        mock_monitor_inst = AsyncMock()
        mock_manager_inst = AsyncMock()
        
        # Configure monitor to raise error during start
        mock_monitor_inst.start_monitoring.side_effect = RuntimeError("Test error")
        mock_monitor_inst.stop_monitoring = AsyncMock()
        mock_monitor.return_value = mock_monitor_inst
        
        # Configure manager
        mock_manager_inst.start_monitoring = AsyncMock()
        mock_manager_inst.stop_monitoring = AsyncMock()
        mock_manager.return_value = mock_manager_inst

        # Start system and expect error
        with pytest.raises(RuntimeError, match="Test error"):
            await error_system.start()

        # Verify cleanup was attempted
        assert mock_monitor_inst.stop_monitoring.called
        assert mock_manager_inst.stop_monitoring.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
