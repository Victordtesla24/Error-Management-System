"""Error fixing module."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional

from .models import ErrorFix, ErrorStatus, ErrorTask


class ErrorFixer:
    """Fix detected errors."""

    def __init__(self):
        """Initialize error fixer."""
        self.logger = logging.getLogger(__name__)
        self._fix_strategies = {
            "SyntaxError": self._fix_syntax_error,
            "ImportError": self._fix_import_error,
            "TypeError": self._fix_type_error,
            "RuntimeError": self._fix_runtime_error,
            "StreamlitError": self._fix_streamlit_error,
        }

    async def fix_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix an error."""
        try:
            # Get fix strategy
            fix_strategy = self._fix_strategies.get(error.error_type)
            if not fix_strategy:
                self.logger.warning(
                    f"No fix strategy for error type: {error.error_type}"
                )
                return None

            # Create backup
            self._backup_file(Path(error.file_path))

            # Apply fix
            fix = await fix_strategy(error)
            if fix and fix.success:
                self.logger.info(f"Fixed error: {error.message}")
                return fix

            return None

        except Exception as e:
            self.logger.error(f"Error fixing error: {str(e)}")
            return None

    def _backup_file(self, file_path: Path) -> None:
        """Create backup of file."""
        try:
            if not file_path.exists():
                return

            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            backup_path = backup_dir / f"{file_path.name}.bak"
            backup_path.write_text(file_path.read_text())

        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")

    async def _fix_syntax_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix syntax error."""
        try:
            file_path = Path(error.file_path)
            content = file_path.read_text().splitlines()
            line = content[error.line_number - 1]

            # Common syntax fixes
            fixes = {
                "invalid syntax": self._fix_invalid_syntax,
                "unexpected indent": self._fix_indentation,
                "expected an indented block": self._fix_missing_indentation,
                "unexpected EOF": self._fix_unexpected_eof,
            }

            for pattern, fix_func in fixes.items():
                if pattern in error.message.lower():
                    fixed_line = fix_func(line)
                    if fixed_line != line:
                        content[error.line_number - 1] = fixed_line
                        file_path.write_text("\n".join(content))
                        return ErrorFix(
                            error_id=error.id,
                            success=True,
                            message=f"Fixed syntax error: {error.message}",
                            changes={"line": fixed_line},
                        )

            return None

        except Exception as e:
            self.logger.error(f"Error fixing syntax error: {str(e)}")
            return None

    async def _fix_import_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix import error."""
        try:
            file_path = Path(error.file_path)
            content = file_path.read_text().splitlines()
            line = content[error.line_number - 1]

            # Check for common import issues
            if "No module named" in error.message:
                module = error.message.split("'")[1]
                # Try to fix relative import
                if "." in module:
                    fixed_line = self._fix_relative_import(line, module)
                    if fixed_line != line:
                        content[error.line_number - 1] = fixed_line
                        file_path.write_text("\n".join(content))
                        return ErrorFix(
                            error_id=error.id,
                            success=True,
                            message=f"Fixed import error: {error.message}",
                            changes={"line": fixed_line},
                        )

            return None

        except Exception as e:
            self.logger.error(f"Error fixing import error: {str(e)}")
            return None

    async def _fix_type_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix type error."""
        try:
            file_path = Path(error.file_path)
            content = file_path.read_text().splitlines()
            line = content[error.line_number - 1]

            # Fix type errors in Error class initialization
            if (
                "Error.__init__() got an unexpected keyword argument 'type'"
                in error.message
            ):
                # Update Error class usage
                if "Error(" in line:
                    fixed_line = line.replace("type=", "error_type=")
                    content[error.line_number - 1] = fixed_line
                    file_path.write_text("\n".join(content))
                    return ErrorFix(
                        error_id=error.id,
                        success=True,
                        message="Fixed Error class type parameter",
                        changes={"line": fixed_line},
                    )

            return None

        except Exception as e:
            self.logger.error(f"Error fixing type error: {str(e)}")
            return None

    async def _fix_runtime_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix runtime error."""
        try:
            file_path = Path(error.file_path)
            content = file_path.read_text().splitlines()
            line = content[error.line_number - 1]

            # Add specific runtime error fixes here
            # For now, just log the error
            self.logger.info(f"Runtime error needs manual fix: {error.message}")
            return None

        except Exception as e:
            self.logger.error(f"Error fixing runtime error: {str(e)}")
            return None

    async def _fix_streamlit_error(self, error: ErrorTask) -> Optional[ErrorFix]:
        """Fix Streamlit error."""
        try:
            file_path = Path(error.file_path)
            content = file_path.read_text().splitlines()
            line = content[error.line_number - 1]

            # Add specific Streamlit error fixes here
            # For now, just log the error
            self.logger.info(f"Streamlit error needs manual fix: {error.message}")
            return None

        except Exception as e:
            self.logger.error(f"Error fixing Streamlit error: {str(e)}")
            return None

    def _fix_invalid_syntax(self, line: str) -> str:
        """Fix invalid syntax."""
        # Add specific syntax fixes here
        return line

    def _fix_indentation(self, line: str) -> str:
        """Fix indentation."""
        # Remove leading spaces in multiples of 4
        return line.lstrip()

    def _fix_missing_indentation(self, line: str) -> str:
        """Fix missing indentation."""
        # Add 4 spaces of indentation
        return "    " + line

    def _fix_unexpected_eof(self, line: str) -> str:
        """Fix unexpected EOF."""
        # Add missing closing bracket/parenthesis
        brackets = {")": "(", "]": "[", "}": "{"}
        for close_bracket, open_bracket in brackets.items():
            if line.count(open_bracket) > line.count(close_bracket):
                return line + close_bracket
        return line

    def _fix_relative_import(self, line: str, module: str) -> str:
        """Fix relative import."""
        # Convert relative import to absolute import
        if line.startswith("from ."):
            parts = line.split(" ")
            if len(parts) >= 4:
                return f"from {module} {parts[2]} {parts[3]}"
        return line
