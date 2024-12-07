"""
Tests for the secure environment component
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from error_management.secure_environment import SecureEnvironment, SecurityError


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    # Convert to real path to handle symlinks
    real_path = os.path.realpath(temp_dir)
    yield real_path
    shutil.rmtree(real_path)


@pytest.fixture
def secure_env(temp_project_dir):
    """Create secure environment instance"""
    return SecureEnvironment(temp_project_dir)


def test_secure_environment_initialization(temp_project_dir):
    """Test secure environment initialization"""
    secure_env = SecureEnvironment(temp_project_dir)
    assert secure_env.security_context is not None
    expected_path = Path(temp_project_dir).resolve()
    assert secure_env.security_context.project_path == expected_path
    assert len(secure_env.security_context.allowed_operations) > 0


def test_invalid_project_path():
    """Test initialization with invalid path"""
    with pytest.raises(SecurityError):
        SecureEnvironment("/nonexistent/path")


def test_project_path_validation(secure_env):
    """Test project path validation"""
    # Valid path
    project_path = str(secure_env.security_context.project_path)
    assert secure_env._validate_project_path(project_path)

    # Invalid path
    assert not secure_env._validate_project_path("/nonexistent/path")


def test_security_token_generation(secure_env):
    """Test security token generation"""
    token = secure_env._generate_security_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_operation_validation(secure_env, temp_project_dir):
    """Test operation validation"""
    # Valid operation and path
    test_file = Path(temp_project_dir) / "test.txt"
    test_file.touch()
    assert secure_env.validate_operation("read", test_file)

    # Invalid operation
    assert not secure_env.validate_operation("invalid_op", test_file)

    # Path outside project
    outside_file = Path("/tmp/outside.txt")
    assert not secure_env.validate_operation("read", outside_file)


def test_get_project_files(secure_env, temp_project_dir):
    """Test getting project files"""
    # Create test files
    test_files = []
    for i in range(3):
        file_path = Path(temp_project_dir) / f"test{i}.py"
        file_path.touch()
        test_files.append(file_path.resolve())

    # Get files
    files = secure_env.get_project_files()
    assert len(files) == 3

    # Verify paths using resolved paths
    project_path = Path(temp_project_dir).resolve()
    file_paths = sorted(str(f.relative_to(project_path)) for f in files)
    expected_paths = sorted(str(f.relative_to(project_path)) for f in test_files)
    assert file_paths == expected_paths


def test_verify_security_token(secure_env):
    """Test security token verification"""
    token = secure_env.security_context.security_token
    assert secure_env.verify_security_token(token)
    assert not secure_env.verify_security_token("invalid-token")


def test_security_context_serialization(secure_env):
    """Test security context serialization"""
    context_dict = secure_env.security_context.to_dict()
    assert isinstance(context_dict, dict)
    assert "project_path" in context_dict
    assert "allowed_operations" in context_dict
    assert "security_token" in context_dict


def test_container_isolation(secure_env):
    """Test container isolation"""
    # Attempt to access system paths
    system_paths = ["/etc", "/usr", "/var"]
    for path in system_paths:
        assert not secure_env.validate_operation("read", Path(path))


@pytest.mark.asyncio
async def test_concurrent_access(secure_env, temp_project_dir):
    """Test concurrent access"""
    # Create test files
    test_files = []
    for i in range(10):
        file_path = Path(temp_project_dir) / f"test{i}.py"
        file_path.touch()
        test_files.append(file_path.resolve())

    # Concurrent validation
    async def validate_files():
        return [secure_env.validate_operation("read", f) for f in test_files]

    results = await asyncio.gather(*[validate_files() for _ in range(5)])
    assert all(all(result) for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
