"""Logging configuration for the error management system."""

import logging
import logging.config
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config() -> Dict[str, Any]:
    """Load logging configuration from config file.

    Returns:
        Dict containing logging configuration
    """
    try:
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("logging", {})
    except Exception as e:
        print(f"Failed to load logging config: {str(e)}")
        return {}


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # Set log file path
        log_file = log_dir / "error_management.log"

        # Try to load config from file first
        config = load_config()

        if config:
            # Update log file path in config
            if "handlers" in config and "file" in config["handlers"]:
                config["handlers"]["file"]["filename"] = str(log_file)

            # Apply configuration
            try:
                logging.config.dictConfig(config)
                logger = logging.getLogger("error_management")
                logger.info("Logging initialized from config file")
                logger.info(f"Log file: {log_file}")
                return
            except Exception as e:
                print(f"Failed to apply logging config: {str(e)}")
                # Fall back to basic config

        # Fall back to basic configuration if config loading fails
        numeric_level = getattr(logging, level.upper(), logging.INFO)

        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),  # Also log to console
            ],
        )

        # Create logger
        logger = logging.getLogger("error_management")
        logger.setLevel(numeric_level)

        # Log startup message
        logger.info(f"Logging initialized at level {level} (basic configuration)")
        logger.info(f"Log file: {log_file}")

    except Exception as e:
        # Last resort fallback if everything fails
        print(f"Failed to initialize logging: {str(e)}")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"error_management.{name}")
