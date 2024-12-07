"""
Integration tests for Error Management System
Tests full system functionality and component interaction
"""

import asyncio
import shutil
import tempfile
from pathlib import Path

import pytest

from error_management.error_manager import ErrorManager
from error_management.file_monitor import FileMonitor
from error_management.secure_environment import SecureEnvironment


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def system_components(temp_project_dir):
    """Create system components for testing"""
    secure_env = SecureEnvironment(temp_project_dir)
    error_manager = ErrorManager(secure_env)
    file_monitor = FileMonitor(secure_env, error_manager)
    return secure_env, error_manager, file_monitor


@pytest.mark.asyncio
async def test_full_system_integration(system_components):
    """Test full system integration"""
    secure_env, error_manager, file_monitor = system_components

    # Start monitoring
    await file_monitor.start_monitoring()

    try:
        # Create test file with error
        test_file = Path(secure_env.security_context.project_path) / "test.py"
        test_file.write_text(
            """
def invalid_function():
    print("Missing closing parenthesis"
    """
        )

        # Wait for error detection
        await asyncio.sleep(1)

        # Verify error was detected
        assert len(error_manager.current_errors) > 0
        assert test_file in error_manager.current_errors
    finally:
        # Cleanup
        await file_monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_security_boundaries(system_components):
    """Test security boundary enforcement"""
    secure_env, error_manager, file_monitor = system_components

    # Start monitoring
    await file_monitor.start_monitoring()

    try:
        # Attempt to access file outside project
        outside_file = Path("/tmp/outside.py")
        if outside_file.exists():
            outside_file.unlink()

        outside_file.write_text("print('test')")

        # Verify access is denied
        assert not secure_env.validate_operation("read", outside_file)
        assert not secure_env.validate_operation("write", outside_file)

        # Cleanup
        outside_file.unlink()
    finally:
        await file_monitor.stop_monitoring()


@pytest.mark.asyncio
async def test_error_fixing_workflow(system_components):
    """Test error detection and fixing workflow"""
    secure_env, error_manager, file_monitor = system_components

    # Start monitoring
    await file_monitor.start_monitoring()

    try:
        # Create file with error
        test_file = Path(secure_env.security_context.project_path) / "test.py"
        test_file.write_text(
            """
def test_function():
    x = 1
    y = 2
    return x + y  # Missing parenthesis
"""
        )

        # Wait for error detection
        await asyncio.sleep(1)

        # Fix error
        test_file.write_text(
            """
def test_function():
    x = 1
    y = 2
    return (x + y)  # Fixed parenthesis
"""
        )

        # Wait for fix verification
        await asyncio.sleep(1)

        # Verify error was fixed
        assert len(error_manager.current_errors) == 0
    finally:
        await file_monitor.stop_monitoring()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
