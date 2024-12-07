"""
Secure Environment Module for Error Management System
Handles project isolation and security context management
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)
logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Custom exception for security-related errors"""

    pass


@dataclass
class SecurityContext:
    """Security context for project operations"""

    project_path: Path
    allowed_operations: List[str]
    security_token: str

    def to_dict(self) -> dict:
        """Convert context to dictionary for serialization"""
        return {
            "project_path": str(self.project_path),
            "allowed_operations": self.allowed_operations,
            "security_token": self.security_token,
        }


class SecureEnvironment:
    """
    Manages the secure environment for error management operations
    Ensures isolation and access control
    """

    def __init__(self, project_path: str):
        """
        Initialize secure environment with project path

        Args:
            project_path: Path to the project directory

        Raises:
            SecurityError: If project path is invalid or access is denied
        """
        self.security_context = self._initialize_security(project_path)
        logger.info(f"Secure environment initialized for {project_path}")

    def _initialize_security(self, project_path: str) -> SecurityContext:
        """
        Initialize security context for the project

        Args:
            project_path: Path to the project directory

        Returns:
            SecurityContext: Initialized security context

        Raises:
            SecurityError: If project path validation fails
        """
        if not self._validate_project_path(project_path):
            raise SecurityError(f"Invalid project path: {project_path}")

        return SecurityContext(
            project_path=Path(project_path).resolve(),
            allowed_operations=["read", "write", "analyze"],
            security_token=self._generate_security_token(),
        )

    def _validate_project_path(self, path: str) -> bool:
        """
        Validate project path for security

        Args:
            path: Path to validate

        Returns:
            bool: True if path is valid, False otherwise
        """
        try:
            abs_path = Path(path).resolve()

            # Check if path exists and is a directory
            if not abs_path.exists():
                abs_path.mkdir(parents=True, exist_ok=True)
            elif not abs_path.is_dir():
                logger.error(f"Path {path} exists but is not a directory")
                return False

            # Check if path is accessible
            try:
                # Just try to list the directory without iterating
                list(abs_path.iterdir())
                return True
            except PermissionError:
                logger.error(f"Permission denied for path {path}")
                return False
            except StopIteration:
                # Empty directory is valid
                return True

            return True

        except (OSError, ValueError) as e:
            logger.error(f"Error validating path {path}: {str(e)}")
            return False

    def _generate_security_token(self) -> str:
        """
        Generate secure token for environment operations

        Returns:
            str: Generated security token
        """
        # Generate a random token
        random_bytes = secrets.token_bytes(32)
        # Create SHA-256 hash
        token_hash = hashlib.sha256(random_bytes).hexdigest()
        return token_hash

    def validate_operation(self, operation: str, path: Path) -> bool:
        """
        Validate if an operation is allowed on a path

        Args:
            operation: Operation to validate
            path: Path to validate operation for

        Returns:
            bool: True if operation is allowed, False otherwise
        """
        try:
            # Check if operation is allowed
            if operation not in self.security_context.allowed_operations:
                logger.error(f"Operation {operation} not allowed")
                return False

            # Resolve and validate path
            abs_path = path.resolve()
            project_path = self.security_context.project_path
            if not abs_path.is_relative_to(project_path):
                logger.error(f"Path {path} outside project directory")
                return False

            return True

        except (OSError, ValueError) as e:
            logger.error(f"Error validating operation: {str(e)}")
            return False

    def get_project_files(self) -> List[Path]:
        """
        Get list of files in project directory

        Returns:
            List[Path]: List of file paths in project

        Raises:
            SecurityError: If access to project directory fails
        """
        try:
            files = []
            project_path = self.security_context.project_path
            for item in project_path.rglob("*"):
                if item.is_file():
                    files.append(item)
            return files
        except (OSError, PermissionError) as e:
            msg = f"Failed to access project files: {str(e)}"
            raise SecurityError(msg)

    def verify_security_token(self, token: str) -> bool:
        """
        Verify if a security token is valid

        Args:
            token: Token to verify

        Returns:
            bool: True if token is valid, False otherwise
        """
        context_token = self.security_context.security_token
        return secrets.compare_digest(token, context_token)


if __name__ == "__main__":
    # Example usage
    try:
        secure_env = SecureEnvironment("./test_project")
        context_dict = secure_env.security_context.to_dict()
        print(f"Security context initialized: {context_dict}")
    except SecurityError as e:
        print(f"Failed to initialize secure environment: {str(e)}")
