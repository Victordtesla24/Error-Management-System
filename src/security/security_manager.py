"""Security manager module."""

import logging
import os
from pathlib import Path
from typing import Union


class SecurityManager:
    """Security manager."""

    def __init__(self, project_root: Path):
        """Initialize security manager."""
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
        self.allowed_operations = {
            "read": self._validate_read,
            "write": self._validate_write,
            "delete": self._validate_delete,
            "execute": self._validate_execute,
        }

    def validate_operation(self, operation: str, path: Union[str, Path]) -> bool:
        """Validate an operation on a path."""
        if operation not in self.allowed_operations:
            self.logger.error(f"Invalid operation: {operation}")
            return False

        path = Path(path)
        try:
            return self.allowed_operations[operation](path)
        except Exception as e:
            self.logger.error(f"Error validating {operation} operation on {path}: {e}")
            return False

    def _validate_read(self, path: Path) -> bool:
        """Validate read operation."""
        try:
            # Check if path exists and is readable
            if not path.exists():
                self.logger.warning(f"Path does not exist: {path}")
                return False

            # Check if path is within project root
            try:
                path.relative_to(self.project_root)
            except ValueError:
                self.logger.warning(f"Path is outside project root: {path}")
                return False

            # Check if path is readable
            return path.is_file() and os.access(path, os.R_OK)
        except Exception as e:
            self.logger.error(f"Error validating read operation: {e}")
            return False

    def _validate_write(self, path: Path) -> bool:
        """Validate write operation."""
        try:
            # Check if parent directory exists and is writable
            parent = path.parent
            if not parent.exists():
                self.logger.warning(f"Parent directory does not exist: {parent}")
                return False

            # Check if path is within project root
            try:
                path.relative_to(self.project_root)
            except ValueError:
                self.logger.warning(f"Path is outside project root: {path}")
                return False

            # Check if path is writable
            return os.access(parent, os.W_OK)
        except Exception as e:
            self.logger.error(f"Error validating write operation: {e}")
            return False

    def _validate_delete(self, path: Path) -> bool:
        """Validate delete operation."""
        try:
            # Check if path exists
            if not path.exists():
                self.logger.warning(f"Path does not exist: {path}")
                return False

            # Check if path is within project root
            try:
                path.relative_to(self.project_root)
            except ValueError:
                self.logger.warning(f"Path is outside project root: {path}")
                return False

            # Check if path is writable (required for deletion)
            return os.access(path.parent, os.W_OK)
        except Exception as e:
            self.logger.error(f"Error validating delete operation: {e}")
            return False

    def _validate_execute(self, path: Path) -> bool:
        """Validate execute operation."""
        try:
            # Check if path exists and is executable
            if not path.exists():
                self.logger.warning(f"Path does not exist: {path}")
                return False

            # Check if path is within project root
            try:
                path.relative_to(self.project_root)
            except ValueError:
                self.logger.warning(f"Path is outside project root: {path}")
                return False

            # Check if path is executable
            return path.is_file() and os.access(path, os.X_OK)
        except Exception as e:
            self.logger.error(f"Error validating execute operation: {e}")
            return False
