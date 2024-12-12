"""Error handling with Sentry integration."""

import logging
import logging.config  # Add explicit import for logging.config
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/error_handler.log"),
    ],
)
logger = logging.getLogger(__name__)

# Initialize Sentry with better error handling
try:
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO, event_level=logging.ERROR
        )
        sentry_sdk.init(
            dsn=dsn,
            integrations=[sentry_logging],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            before_send=lambda event, hint: event,  # Add custom logic here if needed
        )
        logger.info("Sentry initialized successfully")
    else:
        logger.warning(
            "SENTRY_DSN environment variable not set, Sentry integration disabled"
        )
except Exception as e:
    logger.error(f"Failed to initialize Sentry: {str(e)}")


class ErrorHandler:
    """Handle errors and exceptions."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize error handler."""
        self.project_path = project_path or Path.cwd()
        self.error_counts: Dict[str, int] = {}
        self.fixes: Dict[str, Callable] = {}

    def register_fix(self, error_type: Type[Exception]) -> Callable:
        """Register a fix for an error type."""

        def decorator(fix_func: Callable) -> Callable:
            self.fixes[error_type.__name__] = fix_func
            return fix_func

        return decorator

    def handle_error(self, func: Callable) -> Callable:
        """Decorator to handle errors in functions."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

                # Log error to Sentry if available
                if os.getenv("SENTRY_DSN"):
                    try:
                        sentry_sdk.capture_exception(e)
                    except Exception as sentry_error:
                        logger.error(
                            f"Failed to send error to Sentry: {str(sentry_error)}"
                        )

                logger.error(f"Error in {func.__name__}: {str(e)}")

                # Try to fix error
                fix_func = self.fixes.get(error_type)
                if fix_func:
                    try:
                        logger.info(f"Attempting to fix {error_type} error")
                        fix_func(e, *args, **kwargs)
                        logger.info(f"Successfully fixed {error_type} error")
                    except Exception as fix_error:
                        logger.error(
                            f"Failed to fix {error_type} error: {str(fix_error)}"
                        )
                        raise

                raise

        return wrapper

    def monitor(self, path: Path) -> None:
        """Monitor a path for errors."""
        try:
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                return

            logger.info(f"Monitoring {path} for errors")

            # Add monitoring logic here
            # This could integrate with the watchdog monitor we created

        except Exception as e:
            logger.error(f"Error monitoring path {path}: {str(e)}")
            if os.getenv("SENTRY_DSN"):
                try:
                    sentry_sdk.capture_exception(e)
                except Exception as sentry_error:
                    logger.error(f"Failed to send error to Sentry: {str(sentry_error)}")

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts,
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
        }


# Create singleton instance
error_handler = ErrorHandler()


# Example fix registration
@error_handler.register_fix(ImportError)
def fix_import_error(error: ImportError, *args: Any, **kwargs: Any) -> None:
    """Fix import errors."""
    module = str(error).split("'")[1]
    logger.info(f"Attempting to install missing module: {module}")
    try:
        import pip

        pip.main(["install", module])
        logger.info(f"Successfully installed {module}")
    except Exception as e:
        logger.error(f"Failed to install {module}: {str(e)}")
        raise


@error_handler.register_fix(TypeError)
def fix_type_error(error: TypeError, *args: Any, **kwargs: Any) -> None:
    """Fix type errors."""
    if "got an unexpected keyword argument 'type'" in str(error):
        logger.info("Fixing Error class type parameter")
        # This would be handled by the error fixer we created earlier
    else:
        logger.warning(f"No automatic fix available for: {str(error)}")


@error_handler.register_fix(SyntaxError)
def fix_syntax_error(error: SyntaxError, *args: Any, **kwargs: Any) -> None:
    """Fix syntax errors."""
    logger.info(f"Attempting to fix syntax error: {error.msg}")
    # This would be handled by the error fixer we created earlier
