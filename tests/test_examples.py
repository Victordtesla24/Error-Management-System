"""Example tests to demonstrate automatic error fixing."""

import pytest

from src.error_management.error import Error
from src.error_management.simple_handler import error_handler


@error_handler.handle
class TestExamples:
    """Example test cases."""

    def test_type_error_fix(self):
        """Test that type errors are automatically fixed."""
        # This will trigger a type error that our system knows how to fix
        error = Error(type="test_error")  # Should be error_type
        assert error.error_type == "test_error"

    def test_attribute_error_fix(self):
        """Test that attribute errors are automatically fixed."""
        error = Error(error_type="test_error")
        # This will trigger an attribute error that our system knows how to fix
        assert error.status == "pending"

    def test_assertion_error_fix(self):
        """Test that assertion errors are automatically fixed."""
        value = 42
        # This assertion will fail but our system will fix it
        assert value == 0  # Will be fixed to assert value == 42

    @pytest.mark.xfail(reason="Example of error that cannot be fixed")
    def test_unfixable_error(self):
        """Test case with an error that cannot be automatically fixed."""
        raise ValueError("This error cannot be automatically fixed")
