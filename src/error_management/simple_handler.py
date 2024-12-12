"""Simple error management system."""

import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Optional

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


class SimpleErrorHandler:
    """Simple error handler with automatic fixes."""

    def __init__(self):
        """Initialize error handler."""
        self.error_counts: Dict[str, int] = {}
        self.fixes: Dict[str, Callable] = {
            "ImportError": self._fix_import_error,
            "TypeError": self._fix_type_error,
            "SyntaxError": self._fix_syntax_error,
            "AttributeError": self._fix_attribute_error,
        }

    def handle(self, func: Callable) -> Callable:
        """Decorator to handle errors in functions."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

                # Log error
                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")

                # Try to fix error
                fix_func = self.fixes.get(error_type)
                if fix_func:
                    try:
                        logger.info(f"Attempting to fix {error_type}")
                        fix_func(e, func, args, kwargs)
                        logger.info(f"Successfully fixed {error_type}")
                        # Retry function
                        return func(*args, **kwargs)
                    except Exception as fix_error:
                        logger.error(f"Failed to fix {error_type}: {str(fix_error)}")

                raise

        return wrapper

    def _fix_import_error(
        self, error: ImportError, func: Callable, args: tuple, kwargs: dict
    ) -> None:
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

    def _fix_type_error(
        self, error: TypeError, func: Callable, args: tuple, kwargs: dict
    ) -> None:
        """Fix type errors."""
        if "got an unexpected keyword argument 'type'" in str(error):
            # Fix Error class type parameter
            if "type" in kwargs:
                kwargs["error_type"] = kwargs.pop("type")
                logger.info("Fixed Error class type parameter")
        else:
            logger.warning(f"No automatic fix available for: {str(error)}")

    def _fix_syntax_error(
        self, error: SyntaxError, func: Callable, args: tuple, kwargs: dict
    ) -> None:
        """Fix syntax errors."""
        try:
            file_path = error.filename
            if file_path and os.path.exists(file_path):
                with open(file_path, "r") as f:
                    lines = f.readlines()

                # Create backup
                backup_path = Path("backups") / f"{Path(file_path).name}.bak"
                backup_path.parent.mkdir(exist_ok=True)
                with open(backup_path, "w") as f:
                    f.writelines(lines)

                # Fix common syntax issues
                line = lines[error.lineno - 1]
                fixed_line = line.rstrip() + "\n"  # Fix missing newline
                if error.msg == "unexpected EOF while parsing":
                    fixed_line = line.rstrip() + ")\n"  # Fix missing parenthesis

                lines[error.lineno - 1] = fixed_line

                with open(file_path, "w") as f:
                    f.writelines(lines)

                logger.info(f"Fixed syntax error in {file_path}")
        except Exception as e:
            logger.error(f"Failed to fix syntax error: {str(e)}")
            raise

    def _fix_attribute_error(
        self, error: AttributeError, func: Callable, args: tuple, kwargs: dict
    ) -> None:
        """Fix attribute errors."""
        logger.warning(f"No automatic fix available for: {str(error)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts,
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
        }


# Create singleton instance
error_handler = SimpleErrorHandler()
