"""Error detection and analysis module."""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.error_management.models import Error


class ErrorDetector:
    """Detect and analyze errors in code."""

    def __init__(self, project_path: Path):
        """Initialize error detector."""
        self.project_path = project_path
        self.logger = logging.getLogger("error_detector")

        # Common error patterns
        self.error_patterns = {
            "syntax": r"^.*SyntaxError: (.*)$",
            "indentation": r"^.*IndentationError: (.*)$",
            "import": r"^.*ImportError: (.*)$",
            "attribute": r"^.*AttributeError: (.*)$",
            "type": r"^.*TypeError: (.*)$",
            "name": r"^.*NameError: (.*)$",
            "value": r"^.*ValueError: (.*)$",
            "assertion": r"^.*AssertionError: (.*)$",
            "runtime": r"^.*RuntimeError: (.*)$",
        }

    async def analyze_error(self, error_output: str) -> Optional[Dict[str, Any]]:
        """Analyze error output and extract details."""
        try:
            # Extract error type and message
            error_type, message = self._parse_error_message(error_output)
            if not error_type:
                return None

            # Get file and line information
            file_path, line_num = self._extract_location(error_output)
            if not file_path:
                return None

            # Get error context
            context = self._get_error_context(file_path, line_num)
            if not context:
                return None

            # Analyze code for potential fixes
            fixes = await self._analyze_for_fixes(
                error_type, message, file_path, line_num, context
            )

            return {
                "type": error_type,
                "message": message,
                "file": str(file_path),
                "line": line_num,
                "context": context,
                "potential_fixes": fixes,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing error output: {str(e)}")
            return None

    def _parse_error_message(
        self, error_output: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Parse error output for type and message."""
        try:
            for error_type, pattern in self.error_patterns.items():
                match = re.search(pattern, error_output, re.MULTILINE)
                if match:
                    return error_type, match.group(1)
            return None, None
        except Exception as e:
            self.logger.error(f"Error parsing error message: {str(e)}")
            return None, None

    def _extract_location(
        self, error_output: str
    ) -> Tuple[Optional[Path], Optional[int]]:
        """Extract file path and line number from error output."""
        try:
            # Look for file path pattern
            file_match = re.search(r'File "([^"]+)", line (\d+)', error_output)
            if file_match:
                file_path = Path(file_match.group(1))
                line_num = int(file_match.group(2))
                return file_path, line_num
            return None, None
        except Exception as e:
            self.logger.error(f"Error extracting location: {str(e)}")
            return None, None

    def _get_error_context(
        self, file_path: Path, line_num: int
    ) -> Optional[Dict[str, Any]]:
        """Get context around error location."""
        try:
            if not file_path.exists():
                return None

            with open(file_path) as f:
                lines = f.readlines()

            # Get lines around error
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 3)
            context_lines = lines[start:end]

            # Parse code for analysis
            try:
                tree = ast.parse("".join(context_lines))
            except:
                tree = None

            return {
                "lines": context_lines,
                "error_line": lines[line_num - 1] if line_num <= len(lines) else None,
                "ast": tree,
            }

        except Exception as e:
            self.logger.error(f"Error getting context: {str(e)}")
            return None

    async def _analyze_for_fixes(
        self,
        error_type: str,
        message: str,
        file_path: Path,
        line_num: int,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Analyze error for potential fixes."""
        fixes = []
        try:
            if error_type == "syntax":
                fixes.extend(self._analyze_syntax_error(message, context))
            elif error_type == "import":
                fixes.extend(await self._analyze_import_error(message, file_path))
            elif error_type == "attribute":
                fixes.extend(self._analyze_attribute_error(message, context))
            elif error_type == "type":
                fixes.extend(self._analyze_type_error(message, context))
            elif error_type == "assertion":
                fixes.extend(self._analyze_assertion_error(message, context))
        except Exception as e:
            self.logger.error(f"Error analyzing for fixes: {str(e)}")

        return fixes

    def _analyze_syntax_error(
        self, message: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze syntax error for fixes."""
        fixes = []
        try:
            error_line = context.get("error_line", "")

            # Check for common syntax issues
            if ":" not in error_line and error_line.strip().startswith(
                ("def ", "class ", "if ", "for ", "while ")
            ):
                fixes.append(
                    {
                        "type": "add_colon",
                        "description": "Add missing colon",
                        "change": {"type": "append", "text": ":"},
                    }
                )

            if message.startswith("invalid syntax"):
                # Check for missing parentheses
                if "(" in error_line and ")" not in error_line:
                    fixes.append(
                        {
                            "type": "add_parenthesis",
                            "description": "Add missing closing parenthesis",
                            "change": {"type": "append", "text": ")"},
                        }
                    )
                elif ")" in error_line and "(" not in error_line:
                    fixes.append(
                        {
                            "type": "add_parenthesis",
                            "description": "Add missing opening parenthesis",
                            "change": {"type": "prepend", "text": "("},
                        }
                    )

            # Check for string quotes
            if ('"' in error_line and error_line.count('"') % 2 != 0) or (
                "'" in error_line and error_line.count("'") % 2 != 0
            ):
                fixes.append(
                    {
                        "type": "fix_quotes",
                        "description": "Fix string quotes",
                        "change": {
                            "type": "replace",
                            "old": error_line,
                            "new": error_line.replace('"', "'"),
                        },
                    }
                )

        except Exception as e:
            self.logger.error(f"Error analyzing syntax error: {str(e)}")

        return fixes

    async def _analyze_import_error(
        self, message: str, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Analyze import error for fixes."""
        fixes = []
        try:
            if "No module named" in message:
                module_name = message.split("'")[1]

                # Check if module exists in project
                module_path = self.project_path / module_name.replace(".", "/")
                if module_path.exists():
                    fixes.append(
                        {
                            "type": "fix_import_path",
                            "description": f"Update import path for {module_name}",
                            "change": {
                                "type": "prepend",
                                "text": f"from {module_name} import ",
                            },
                        }
                    )
                else:
                    # Suggest pip install
                    fixes.append(
                        {
                            "type": "install_package",
                            "description": f"Install missing package {module_name}",
                            "change": {
                                "type": "command",
                                "command": f"pip install {module_name}",
                            },
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing import error: {str(e)}")

        return fixes

    def _analyze_attribute_error(
        self, message: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze attribute error for fixes."""
        fixes = []
        try:
            if "has no attribute" in message:
                # Extract object and missing attribute
                parts = message.split("'")
                if len(parts) >= 3:
                    obj_name = parts[0].strip()
                    missing_attr = parts[1]

                    # Check for typos in attribute name
                    if context.get("ast"):
                        for node in ast.walk(context["ast"]):
                            if isinstance(node, ast.Attribute):
                                if self._similar_names(node.attr, missing_attr):
                                    fixes.append(
                                        {
                                            "type": "fix_attribute_name",
                                            "description": f"Fix attribute name typo: {missing_attr} -> {node.attr}",
                                            "change": {
                                                "type": "replace",
                                                "old": missing_attr,
                                                "new": node.attr,
                                            },
                                        }
                                    )

                    # Suggest adding property
                    fixes.append(
                        {
                            "type": "add_property",
                            "description": f"Add missing attribute {missing_attr}",
                            "change": {
                                "type": "append",
                                "text": f"\n    {missing_attr} = None",
                            },
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing attribute error: {str(e)}")

        return fixes

    def _analyze_type_error(
        self, message: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze type error for fixes."""
        fixes = []
        try:
            error_line = context.get("error_line", "")

            if "must be str, not" in message:
                fixes.append(
                    {
                        "type": "add_str_conversion",
                        "description": "Convert value to string",
                        "change": {"type": "wrap", "text": "str()"},
                    }
                )
            elif "must be int, not" in message:
                fixes.append(
                    {
                        "type": "add_int_conversion",
                        "description": "Convert value to integer",
                        "change": {"type": "wrap", "text": "int()"},
                    }
                )
            elif "not callable" in message:
                # Check for missing parentheses
                if "(" not in error_line:
                    fixes.append(
                        {
                            "type": "add_call",
                            "description": "Add function call parentheses",
                            "change": {"type": "append", "text": "()"},
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing type error: {str(e)}")

        return fixes

    def _analyze_assertion_error(
        self, message: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze assertion error for fixes."""
        fixes = []
        try:
            error_line = context.get("error_line", "")

            if "assert" in error_line:
                # Check for common assertion patterns
                if "==" in error_line:
                    fixes.append(
                        {
                            "type": "fix_assertion",
                            "description": "Update assertion to use assertEqual",
                            "change": {
                                "type": "replace",
                                "old": error_line,
                                "new": error_line.replace(
                                    "assert", "self.assertEqual("
                                ),
                            },
                        }
                    )
                elif "True" in error_line:
                    fixes.append(
                        {
                            "type": "fix_assertion",
                            "description": "Update assertion to use assertTrue",
                            "change": {
                                "type": "replace",
                                "old": error_line,
                                "new": error_line.replace("assert", "self.assertTrue("),
                            },
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error analyzing assertion error: {str(e)}")

        return fixes

    def _similar_names(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (possible typos)."""
        try:
            if abs(len(name1) - len(name2)) > 2:
                return False

            # Calculate Levenshtein distance
            m = len(name1)
            n = len(name2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]

            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if name1[i - 1] == name2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = 1 + min(
                            dp[i - 1][j],  # deletion
                            dp[i][j - 1],  # insertion
                            dp[i - 1][j - 1],
                        )  # replacement

            return dp[m][n] <= 2  # Allow up to 2 edits

        except Exception as e:
            self.logger.error(f"Error comparing names: {str(e)}")
            return False
