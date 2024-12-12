"""File analyzer module for error management system."""

import os
from pathlib import Path
from typing import Dict, List, Optional


class FileAnalyzer:
    """Analyzes files for potential issues and code quality."""

    def __init__(self, base_path: str = "."):
        """Initialize the file analyzer.

        Args:
            base_path: Base path to analyze files from
        """
        self.base_path = Path(base_path)
        self.file_stats: Dict[str, Dict] = {}

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single file for potential issues.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dict containing analysis results
        """
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}

        stats = {
            "size": path.stat().st_size,
            "lines": 0,
            "imports": [],
            "classes": [],
            "functions": [],
            "issues": [],
        }

        try:
            with open(path) as f:
                content = f.read()
                lines = content.split("\n")
                stats["lines"] = len(lines)

                # Basic analysis
                if stats["lines"] > 500:
                    stats["issues"].append("File too long")

                if stats["size"] > 1_000_000:  # 1MB
                    stats["issues"].append("File too large")

        except Exception as e:
            stats["error"] = str(e)

        self.file_stats[str(path)] = stats
        return stats

    def analyze_directory(self, dir_path: Optional[str] = None) -> Dict[str, Dict]:
        """Analyze all files in a directory recursively.

        Args:
            dir_path: Directory path to analyze, defaults to base_path

        Returns:
            Dict mapping file paths to their analysis results
        """
        if dir_path is None:
            dir_path = self.base_path

        path = Path(dir_path)
        if not path.exists():
            return {"error": "Directory not found"}

        results = {}
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    results[str(file_path)] = self.analyze_file(file_path)

        return results

    def get_file_stats(self, file_path: str) -> Dict:
        """Get analysis results for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            Dict containing analysis results if available
        """
        return self.file_stats.get(str(Path(file_path)), {})

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get analysis results for all analyzed files.

        Returns:
            Dict mapping file paths to their analysis results
        """
        return self.file_stats

    def get_issues(self) -> List[Dict]:
        """Get list of all issues found across analyzed files.

        Returns:
            List of dicts containing file paths and their issues
        """
        issues = []
        for file_path, stats in self.file_stats.items():
            if stats.get("issues"):
                issues.append({"file": file_path, "issues": stats["issues"]})
        return issues
