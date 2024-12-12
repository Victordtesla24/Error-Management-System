"""Error class for error management system."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from .models import ErrorFix, ErrorSeverity, ErrorStatus


@dataclass
class Error:
    """Error class representing a detected error."""

    error_type: str
    message: str = ""
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid4()))
    severity: str = ErrorSeverity.HIGH.value
    status: str = ErrorStatus.PENDING.value
    column: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fixed_at: Optional[datetime] = None
    fix: Optional[ErrorFix] = None

    def __post_init__(self):
        """Post initialization hook."""
        # Handle type parameter for backward compatibility
        if hasattr(self, "type"):
            self.error_type = getattr(self, "type")
            delattr(self, "type")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "id": self.id,
            "error_type": self.error_type,
            "message": self.message,
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity,
            "status": self.status,
            "context": self.context,
            "traceback": self.traceback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None,
            "fix": self.fix.to_dict() if self.fix else None,
        }

    def update_status(self, status: str) -> None:
        """Update error status."""
        self.status = status
        self.updated_at = datetime.now()

    def mark_as_fixed(self, fix: ErrorFix) -> None:
        """Mark error as fixed."""
        self.status = ErrorStatus.FIXED.value
        self.fixed_at = datetime.now()
        self.updated_at = datetime.now()
        self.fix = fix
