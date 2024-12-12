"""Error context analysis module."""

import ast
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import ErrorContext


class ErrorContextAnalyzer:
    """Analyze error context."""

    def __init__(self):
        """Initialize error context analyzer."""
        self.logger = logging.getLogger("error_context")

    async def get_context(
        self, file_path: str, line_number: int, error_message: str
    ) -> ErrorContext:
        """Get error context."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read file content
            with open(path) as f:
                content = f.read()
                lines = content.splitlines()

            # Get line content
            line_content = (
                lines[line_number - 1] if 0 < line_number <= len(lines) else ""
            )

            # Parse code
            try:
                tree = ast.parse(content)
            except SyntaxError:
                tree = None

            # Get context details
            function_name, class_name = self._get_scope_names(tree, line_number)
            imports = self._get_imports(tree)
            variables = self._get_variables(tree, line_number)
            related_files = await self._get_related_files(path, imports)
            dependencies = self._get_dependencies(path)

            return ErrorContext(
                file_content=content,
                line_content=line_content,
                line_number=line_number,
                function_name=function_name,
                class_name=class_name,
                imports=imports,
                variables=variables,
                related_files=related_files,
                dependencies=dependencies,
            )

        except Exception as e:
            self.logger.error(f"Failed to get error context: {str(e)}")
            raise

    def _get_scope_names(
        self, tree: Optional[ast.AST], line_number: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get function and class names for line."""
        try:
            if not tree:
                return None, None

            function_name = None
            class_name = None

            for node in ast.walk(tree):
                if not hasattr(node, "lineno"):
                    continue

                # Check if line is within node's scope
                if node.lineno <= line_number <= self._get_end_line(node):
                    if isinstance(node, ast.FunctionDef):
                        function_name = node.name
                    elif isinstance(node, ast.ClassDef):
                        class_name = node.name

            return function_name, class_name

        except Exception as e:
            self.logger.error(f"Failed to get scope names: {str(e)}")
            return None, None

    def _get_end_line(self, node: ast.AST) -> int:
        """Get end line number for node."""
        try:
            return max(
                getattr(node, "lineno", 0),
                *(self._get_end_line(child) for child in ast.iter_child_nodes(node)),
            )
        except Exception:
            return getattr(node, "lineno", 0)

    def _get_imports(self, tree: Optional[ast.AST]) -> List[str]:
        """Get imports from AST."""
        try:
            if not tree:
                return []

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(f"import {name.name}")
                elif isinstance(node, ast.ImportFrom):
                    names = ", ".join(n.name for n in node.names)
                    imports.append(f"from {node.module} import {names}")

            return imports

        except Exception as e:
            self.logger.error(f"Failed to get imports: {str(e)}")
            return []

    def _get_variables(
        self, tree: Optional[ast.AST], line_number: int
    ) -> Dict[str, Any]:
        """Get variables in scope."""
        try:
            if not tree:
                return {}

            variables = {}

            class VariableVisitor(ast.NodeVisitor):
                def visit_Assign(self, node):
                    if hasattr(node, "lineno") and node.lineno < line_number:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                try:
                                    value = ast.literal_eval(node.value)
                                    variables[target.id] = value
                                except (ValueError, SyntaxError):
                                    variables[target.id] = "..."

            VariableVisitor().visit(tree)
            return variables

        except Exception as e:
            self.logger.error(f"Failed to get variables: {str(e)}")
            return {}

    async def _get_related_files(
        self, file_path: Path, imports: List[str]
    ) -> List[str]:
        """Get related files based on imports."""
        try:
            related = []
            project_root = file_path.parent

            for imp in imports:
                if imp.startswith("from "):
                    # Handle from imports
                    parts = imp.split(" ")
                    if len(parts) >= 4:
                        module = parts[1]
                        module_path = project_root / f"{module.replace('.', '/')}.py"
                        if module_path.exists():
                            related.append(str(module_path))
                else:
                    # Handle direct imports
                    module = imp.split(" ")[1]
                    module_path = project_root / f"{module.replace('.', '/')}.py"
                    if module_path.exists():
                        related.append(str(module_path))

            return related

        except Exception as e:
            self.logger.error(f"Failed to get related files: {str(e)}")
            return []

    def _get_dependencies(self, file_path: Path) -> Dict[str, str]:
        """Get project dependencies."""
        try:
            dependencies = {}

            # Check for requirements.txt
            req_file = file_path.parent / "requirements.txt"
            if req_file.exists():
                with open(req_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "==" in line:
                                package, version = line.split("==")
                                dependencies[package] = version
                            elif ">=" in line:
                                package, version = line.split(">=")
                                dependencies[package] = f">={version}"

            return dependencies

        except Exception as e:
            self.logger.error(f"Failed to get dependencies: {str(e)}")
            return {}
