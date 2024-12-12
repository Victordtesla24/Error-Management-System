"""Error detection module."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from uuid import uuid4

from .models import ErrorSeverity, ErrorTask


class ErrorDetector:
    """Detect errors in source code files."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize error detector."""
        self.logger = logging.getLogger(__name__)
        self._project_path = project_path or Path.cwd()
        self._monitored_paths: Set[Path] = set()
        self._error_patterns = {
            "SyntaxError": r"SyntaxError: (.*)",
            "ImportError": r"ImportError: (.*)",
            "TypeError": r"TypeError: (.*)",
            "RuntimeError": r"\[ERROR\] (.*)",
            "StreamlitError": r"\[WARNING\] Uncaught app exception",
        }

    def add_monitored_path(self, path: Path) -> None:
        """Add path to monitor for errors."""
        if path.exists():
            self._monitored_paths.add(path)
            self.logger.info(f"Added path to monitor: {path}")
        else:
            self.logger.warning(f"Path does not exist: {path}")

    def scan_for_errors(self) -> List[ErrorTask]:
        """Scan monitored paths for errors."""
        errors: List[ErrorTask] = []

        for path in self._monitored_paths:
            if not path.exists():
                continue

            if path.is_file():
                file_errors = self._scan_file(path)
                errors.extend(file_errors)
            else:
                for file_path in path.rglob("*.py"):
                    file_errors = self._scan_file(file_path)
                    errors.extend(file_errors)

        return errors

    def _scan_file(self, file_path: Path) -> List[ErrorTask]:
        """Scan a single file for errors."""
        errors: List[ErrorTask] = []
        try:
            content = file_path.read_text()
            line_number = 1

            for line in content.splitlines():
                for error_type, pattern in self._error_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        error = ErrorTask(
                            id=str(uuid4()),
                            error_type=error_type,
                            message=(
                                match.group(1) if match.groups() else match.group(0)
                            ),
                            file_path=str(file_path),
                            line_number=line_number,
                            severity=ErrorSeverity.HIGH.value,
                            context={"line": line},
                        )
                        errors.append(error)
                line_number += 1

        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {str(e)}")

        return errors

    def _get_error_context(self, file_path: Path, line_number: int) -> Dict[str, str]:
        """Get context around error line."""
        try:
            lines = file_path.read_text().splitlines()
            start = max(0, line_number - 3)
            end = min(len(lines), line_number + 3)

            context = {
                "before": "\n".join(lines[start : line_number - 1]),
                "line": lines[line_number - 1],
                "after": "\n".join(lines[line_number:end]),
            }
            return context

        except Exception as e:
            self.logger.error(f"Error getting context: {str(e)}")
            return {}
