"""
Tests for the error management component
"""

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from error_management.error_manager import ErrorContext, ErrorManager
from error_management.secure_environment import SecureEnvironment

# Configure test logging
logging.basicConfig(level=logging.DEBUG)


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


@pytest.mark.asyncio
async def test_error_manager_initialization(error_manager):
    """Test error manager initialization"""
    assert error_manager.secure_env is not None
    assert error_manager.current_errors == {}
    assert error_manager._running is False


@pytest.mark.asyncio
async def test_monitoring_start_stop(error_manager):
    """Test starting and stopping monitoring"""
    # Start monitoring
    monitor_task = asyncio.create_task(error_manager.start_monitoring())

    # Wait briefly for monitoring to start
    await asyncio.sleep(0.1)
    assert error_manager._running is True

    # Stop monitoring
    await error_manager.stop_monitoring()
    assert error_manager._running is False

    # Cancel the monitoring task
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_python_file_analysis(error_manager, temp_project_dir):
    """Test Python file analysis"""
    # Create a Python file with a syntax error
    test_file = Path(temp_project_dir) / "test.py"
    test_file.write_text(
        """
def invalid_function():
    print("Missing closing parenthesis"
    """
    )

    # Analyze the file
    await error_manager._analyze_python_file(test_file)

    # Check if error was detected
    assert test_file in error_manager.current_errors
    assert len(error_manager.current_errors[test_file]) > 0

    # Verify error context
    error = error_manager.current_errors[test_file][0]
    assert isinstance(error, ErrorContext)
    assert error.error_type == "syntax_error"
    assert error.severity == 1


@pytest.mark.asyncio
async def test_error_handling(error_manager, temp_project_dir):
    """Test error handling process"""
    # Create a test error context
    test_file = Path(temp_project_dir) / "test.py"
    test_file.touch()

    error = ErrorContext(
        file_path=test_file,
        error_type="test_error",
        code_context="test code",
        line_number=1,
        severity=1,
    )

    # Handle the error
    await error_manager._handle_error(error)

    # Verify error was recorded
    assert test_file in error_manager.current_errors
    assert len(error_manager.current_errors[test_file]) == 1
    assert error_manager.current_errors[test_file][0] == error


@pytest.mark.asyncio
async def test_duplicate_error_handling(error_manager, temp_project_dir):
    """Test handling of duplicate errors"""
    # Create a test file and error
    test_file = Path(temp_project_dir) / "test.py"
    test_file.touch()

    error = ErrorContext(
        file_path=test_file,
        error_type="test_error",
        code_context="test code",
        line_number=1,
        severity=1,
    )

    # Handle the same error twice
    await error_manager._handle_error(error)
    await error_manager._handle_error(error)

    # Verify error was only recorded once
    assert len(error_manager.current_errors[test_file]) == 1


@pytest.mark.asyncio
async def test_error_fixing_security(error_manager, temp_project_dir):
    """Test error fixing security boundaries"""
    # Create a file outside project directory
    outside_file = Path(tempfile.gettempdir()) / "outside.py"
    outside_file.touch()

    error = ErrorContext(
        file_path=outside_file,
        error_type="test_error",
        code_context="test code",
        line_number=1,
        severity=1,
    )

    # Attempt to fix error in file outside project
    await error_manager._attempt_fix(error)

    # Verify no changes were made
    assert outside_file not in error_manager.current_errors

    # Cleanup
    outside_file.unlink()


@pytest.mark.asyncio
async def test_concurrent_error_handling(error_manager, temp_project_dir):
    """Test concurrent error handling"""
    # Create test files and errors
    test_files = []
    errors = []

    for i in range(5):
        test_file = Path(temp_project_dir) / f"test{i}.py"
        test_file.touch()
        test_files.append(test_file)

        error = ErrorContext(
            file_path=test_file,
            error_type=f"test_error_{i}",
            code_context="test code",
            line_number=1,
            severity=1,
        )
        errors.append(error)

    # Handle errors concurrently
    await asyncio.gather(*[error_manager._handle_error(error) for error in errors])

    # Verify all errors were recorded
    for test_file, error in zip(test_files, errors):
        assert test_file in error_manager.current_errors
        assert error in error_manager.current_errors[test_file]


@pytest.mark.asyncio
async def test_error_context_validation(error_manager, temp_project_dir):
    """Test error context validation"""
    test_file = Path(temp_project_dir) / "test.py"
    test_file.write_text(
        """
def valid_function():
    print("This is valid Python code")
    """
    )

    # Create error context
    error = ErrorContext(
        file_path=test_file,
        error_type="test_error",
        code_context="def valid_function():",
        line_number=2,
        severity=1,
    )

    # Verify context understanding
    assert error_manager._understand_context(error) is True


def test_get_current_errors(error_manager, temp_project_dir):
    """Test getting current errors"""
    # Verify initial state
    errors = error_manager.get_current_errors()
    assert isinstance(errors, dict)
    assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
