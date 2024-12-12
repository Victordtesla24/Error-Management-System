"""Runtime error fixing system."""

import logging
import sys
import traceback
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/runtime_fixer.log"),
    ],
)
logger = logging.getLogger(__name__)


class RuntimeFixer:
    """Fix errors at runtime."""

    def __init__(self):
        """Initialize runtime fixer."""
        self.fixes: Dict[str, Callable] = {}
        self.error_counts: Dict[str, int] = {}
        self._register_default_fixes()

    def _register_default_fixes(self):
        """Register default error fixes."""

        # Import errors
        @self.register_fix(ImportError)
        def fix_import_error(error: ImportError, **kwargs):
            module = str(error).split("'")[1]
            logger.info(f"Installing missing module: {module}")
            try:
                import pip

                pip.main(["install", module])
                return True
            except Exception as e:
                logger.error(f"Failed to install {module}: {str(e)}")
                return False

        # Type errors
        @self.register_fix(TypeError)
        def fix_type_error(error: TypeError, **kwargs):
            if "got an unexpected keyword argument 'type'" in str(error):
                if "kwargs" in kwargs:
                    if "type" in kwargs["kwargs"]:
                        kwargs["kwargs"]["error_type"] = kwargs["kwargs"].pop("type")
                        return True
            return False

        # Attribute errors
        @self.register_fix(AttributeError)
        def fix_attribute_error(error: AttributeError, **kwargs):
            if "has no attribute 'ErrorContext'" in str(error):
                self._create_error_context()
                return True
            return False

    def register_fix(self, error_type: Type[Exception]) -> Callable:
        """Register a fix for an error type."""

        def decorator(fix_func: Callable) -> Callable:
            self.fixes[error_type.__name__] = fix_func
            return fix_func

        return decorator

    def auto_fix(self, func: Callable) -> Callable:
        """Decorator to automatically fix errors."""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")

                # Try to fix error
                fix_func = self.fixes.get(error_type)
                if fix_func:
                    try:
                        logger.info(f"Attempting to fix {error_type}")
                        if fix_func(e, func=func, args=args, kwargs=kwargs):
                            logger.info(f"Successfully fixed {error_type}")
                            # Retry function
                            return func(*args, **kwargs)
                        else:
                            logger.warning(f"Could not fix {error_type}")
                    except Exception as fix_error:
                        logger.error(f"Error during fix: {str(fix_error)}")

                raise

        return wrapper

    def _create_error_context(self):
        """Create ErrorContext model."""
        models_path = Path("src/error_management/models.py")
        content = '''"""Error management models."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

@dataclass
class ErrorContext:
    """Context information for an error."""
    file_path: Path
    line_number: int
    function_name: str
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: datetime = datetime.now()
    additional_info: Optional[Dict] = None
'''
        models_path.write_text(content)
        logger.info("Created ErrorContext model")

    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts,
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
        }


# Create singleton instance
runtime_fixer = RuntimeFixer()
