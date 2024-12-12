"""Agent test package.

This package contains tests for the agent monitoring and management functionality.
Tests are organized into the following modules:

- test_agent_lifecycle.py: Tests for agent startup, shutdown, and lifecycle management
- test_agent_monitoring.py: Tests for metrics collection and monitoring functionality
- test_task_management.py: Tests for task assignment and execution
- fixtures.py: Shared test fixtures and utilities

The tests use pytest and pytest-asyncio for async testing support.
"""

from .fixtures import cleanup_monitor, mock_services, monitor, test_project_path

__all__ = ["test_project_path", "mock_services", "monitor", "cleanup_monitor"]
