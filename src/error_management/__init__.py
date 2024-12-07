"""
Error Management System Package
Provides autonomous error detection and fixing capabilities
"""

from .error_manager import ErrorContext, ErrorManager
from .secure_environment import SecureEnvironment, SecurityContext, SecurityError

__version__ = "0.1.0"
__all__ = [
    "SecureEnvironment",
    "SecurityError",
    "SecurityContext",
    "ErrorManager",
    "ErrorContext",
]
