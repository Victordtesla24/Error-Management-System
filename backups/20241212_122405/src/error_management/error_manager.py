"""Error management module."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ErrorModel:
    """Model representing an error."""

    id: str
    type: str
    message: str
    file: str
    line: int
    timestamp: datetime
    status: str = "new"
    fix_attempts: int = 0
    resolved: bool = False
    resolution: Optional[str] = None


class ErrorManager:
    """Manages error detection and resolution."""

    def __init__(self, base_path: str = "."):
        """Initialize error manager."""
        self.base_path = base_path
        self.errors: Dict[str, ErrorModel] = {}
        self._lock = asyncio.Lock()
        self.running = False
        self.issues = {}
        self.issues_by_date = {}
        self.last_update = datetime.now()
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for error manager."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure file handler
        fh = logging.FileHandler(log_dir / "error_manager.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)

        # Add handler if not already added
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)

    async def start(self):
        """Start the error manager."""
        async with self._lock:
            self.running = True
            logger.info("Error manager started")

    async def stop(self):
        """Stop the error manager."""
        async with self._lock:
            self.running = False
            logger.info("Error manager stopped")

    async def add_error(self, error: ErrorModel):
        """Add a new error."""
        async with self._lock:
            self.errors[error.id] = error
            logger.info(f"Added error {error.id}: {error.message}")

    async def get_error(self, error_id: str) -> Optional[ErrorModel]:
        """Get error by ID."""
        async with self._lock:
            return self.errors.get(error_id)

    async def get_errors(self) -> List[ErrorModel]:
        """Get all errors."""
        async with self._lock:
            return list(self.errors.values())

    async def mark_resolved(self, error_id: str, resolution: str):
        """Mark an error as resolved."""
        async with self._lock:
            if error := self.errors.get(error_id):
                error.resolved = True
                error.resolution = resolution
                error.status = "resolved"
                logger.info(f"Marked error {error_id} as resolved")

    async def increment_fix_attempts(self, error_id: str):
        """Increment fix attempts for an error."""
        async with self._lock:
            if error := self.errors.get(error_id):
                error.fix_attempts += 1
                logger.info(f"Incremented fix attempts for error {error_id}")

    def add_issue(self, file: str, issue: str, line: int = None):
        """Add an issue to tracking."""
        if file not in self.issues:
            self.issues[file] = []

        issue_data = {
            "description": issue,
            "line": line,
            "timestamp": datetime.now().isoformat(),
        }
        self.issues[file].append(issue_data)

        # Track by date
        date_key = datetime.now().date().isoformat()
        if date_key not in self.issues_by_date:
            self.issues_by_date[date_key] = 0
        self.issues_by_date[date_key] += 1

        self.last_update = datetime.now()
        logger.info(f"Added issue for {file}: {issue}")

    def remove_issue(self, file: str, issue_index: int):
        """Remove an issue from tracking."""
        if file in self.issues and 0 <= issue_index < len(self.issues[file]):
            issue = self.issues[file].pop(issue_index)

            # Update date tracking
            if issue.get("timestamp"):
                date_key = datetime.fromisoformat(issue["timestamp"]).date().isoformat()
                if (
                    date_key in self.issues_by_date
                    and self.issues_by_date[date_key] > 0
                ):
                    self.issues_by_date[date_key] -= 1

            if not self.issues[file]:
                del self.issues[file]

            self.last_update = datetime.now()
            logger.info(f"Removed issue {issue_index} from {file}")

    def get_issues(self) -> List[Dict]:
        """Get list of issues by file."""
        issues = {}
        for error in self.errors.values():
            if not error.resolved:
                if error.file not in issues:
                    issues[error.file] = []
                issues[error.file].append(error.message)

        return [{"file": k, "issues": v} for k, v in issues.items()]

    def get_error_stats(self) -> Dict:
        """Get error statistics."""
        total = len(self.errors)
        resolved = len([e for e in self.errors.values() if e.resolved])
        unresolved = total - resolved

        by_type = {}
        by_file = {}

        for error in self.errors.values():
            by_type[error.type] = by_type.get(error.type, 0) + 1
            by_file[error.file] = by_file.get(error.file, 0) + 1

        return {
            "total_issues": total,
            "resolved_issues": resolved,
            "unresolved_issues": unresolved,
            "issues_by_type": by_type,
            "issues_by_file": by_file,
            "timestamp": datetime.now().isoformat(),
        }

    def cleanup_old_issues(self, days: int = 30):
        """Clean up issues older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        for file in list(self.issues.keys()):
            self.issues[file] = [
                issue
                for issue in self.issues[file]
                if datetime.fromisoformat(issue["timestamp"]) >= cutoff
            ]
            if not self.issues[file]:
                del self.issues[file]
