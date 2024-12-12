"""Secure environment module."""

import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Set

if TYPE_CHECKING:
    from src.error_management.models import Error

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Security related error."""

    pass


class SecureEnvironment:
    """Manages secure file operations within project boundaries."""

    EXCLUDED_PATTERNS = [
        r"/node_modules/",  # Added path separators
        r"/\.git/",
        r"/\.pytest_cache/",
        r"/__pycache__/",
        r"/\.venv/",
        r"/venv/",
        r"/\.env/",
        r"/site-packages/",
        r"/\.idea/",
        r"/\.vscode/",
    ]

    DANGEROUS_PATTERNS = [
        r"os\.system",
        r"subprocess\.call",
        r"eval\(",
        r"exec\(",
        r"__import__",
    ]

    def __init__(self, project_root: Path):
        """Initialize secure environment.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        if not self.project_root.exists():
            raise SecurityError(f"Project root does not exist: {self.project_root}")
        if not self.project_root.is_dir():
            raise SecurityError(f"Project root is not a directory: {self.project_root}")

    def _is_excluded(self, path: Path) -> bool:
        """Check if path matches excluded patterns."""
        path_str = str(path)
        return any(re.search(pattern, path_str) for pattern in self.EXCLUDED_PATTERNS)

    def is_file_allowed(self, file_path: Path) -> bool:
        """Check if file is allowed for operations.

        Args:
            file_path: Path to file

        Returns:
            bool: Whether file is allowed
        """
        try:
            file_path = Path(file_path).resolve()

            # Check if file is within project boundary
            try:
                file_path.relative_to(self.project_root)
            except ValueError:
                return False

            # Check excluded patterns
            if self._is_excluded(file_path):
                logger.warning(f"File matches excluded pattern: {file_path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking file allowance: {e}")
            return False

    def _is_file_in_project(self, file_path: Path) -> bool:
        """Check if file is within project boundary."""
        return self.is_file_allowed(file_path)

    def validate_operation(self, operation: str, file_path: Path) -> bool:
        """Validate file operation.

        Args:
            operation: Operation type (read/write)
            file_path: Path to file

        Returns:
            bool: Whether operation is allowed
        """
        try:
            if operation not in ["read", "write"]:
                logger.warning(f"Invalid operation: {operation}")
                return False

            file_path = Path(file_path).resolve()

            if self._is_excluded(file_path):
                logger.warning(f"File matches excluded pattern: {file_path}")
                return False

            if not self.is_file_allowed(file_path):
                logger.info(f"Skipping virtual environment file: {file_path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating operation: {e}")
            return False

    def verify_fix(self, error: "Error", fix_content: str) -> bool:
        """Verify fix is safe to apply.

        Args:
            error: Error being fixed
            fix_content: Content of the fix

        Returns:
            bool: Whether fix is safe
        """
        try:
            if not self.is_file_allowed(error.file_path):
                return False

            # Check for dangerous patterns
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, fix_content):
                    logger.warning("Fix contains dangerous code patterns")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error verifying fix: {e}")
            return False

    def get_project_files(self) -> List[Path]:
        """Get all files in project directory.

        Returns:
            List of file paths
        """
        files = []
        try:
            for root, _, filenames in os.walk(self.project_root):
                root_path = Path(root)
                if self._is_excluded(root_path):
                    continue

                for filename in filenames:
                    file_path = root_path / filename
                    if self.is_file_allowed(file_path):
                        files.append(file_path)

        except Exception as e:
            logger.error(f"Error getting project files: {e}")

        return files
