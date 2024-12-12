"""
Configuration classes for error management system
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    max_file_size: int = 1024 * 1024  # 1MB
    allowed_imports: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    sandbox_timeout: int = 5  # seconds


@dataclass
class ErrorManagerConfig:
    scan_interval: int = 60
    max_errors_per_file: int = 100
    cache_size: int = 1000
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ignore_patterns: List[str] = field(default_factory=list)
    excluded_patterns: List[str] = field(
        default_factory=list
    )  # Patterns for files to exclude from scanning
    test_requirements: Dict[str, List[str]] = field(default_factory=dict)


class ConfigManager:
    """Manages system configuration."""

    @staticmethod
    def load_config(path: Optional[str] = None) -> ErrorManagerConfig:
        if not path:
            return ErrorManagerConfig()

        try:
            with open(path, "r") as f:
                config_data = yaml.safe_load(f)
            return ErrorManagerConfig(**config_data)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return ErrorManagerConfig()


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from file or return default configuration.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Dict containing configuration settings
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # Return default configuration if no file provided or file doesn't exist
    return {
        "project_path": os.getcwd(),
        "file_patterns": ["*.py", "*.js"],
        "log_level": "INFO",
        "monitoring_interval": 1,
    }
