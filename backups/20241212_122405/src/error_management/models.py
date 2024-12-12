"""Models for error management system."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorStatus(Enum):
    """Error status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    FAILED = "failed"


class ErrorType(Enum):
    """Error types."""

    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGICAL = "logical"
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    MEMORY = "memory"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    OTHER = "other"


@dataclass
class ErrorContext:
    """Error context information."""

    file_content: str
    line_content: str
    line_number: int
    function_name: Optional[str]
    class_name: Optional[str]
    imports: List[str]
    variables: Dict[str, Any]
    related_files: List[str]
    dependencies: Dict[str, str]


@dataclass
class ErrorFix:
    """Error fix result."""

    error_id: str
    success: bool
    message: str
    changes: Dict[str, Any]
    fix_type: str
    backup_path: Optional[str] = None
    fixed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert fix to dictionary."""
        return {
            "error_id": self.error_id,
            "success": self.success,
            "message": self.message,
            "changes": self.changes,
            "fix_type": self.fix_type,
            "backup_path": self.backup_path,
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None,
        }


@dataclass
class ErrorModel:
    """Error information."""

    id: str
    error_type: str
    message: str
    file_path: str
    line_number: int
    severity: str = ErrorSeverity.HIGH.value
    status: str = ErrorStatus.PENDING.value
    column: Optional[int] = None
    traceback: Optional[str] = None
    fix_attempts: int = 0
    max_retries: int = 3
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "id": self.id,
            "error_type": self.error_type,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity,
            "status": self.status,
            "traceback": self.traceback,
            "fix_attempts": self.fix_attempts,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class ErrorReport:
    """Error report."""

    error: ErrorModel
    fix: Optional[ErrorFix]
    context: ErrorContext
    timestamp: datetime
    report_type: str
    status: str
    metrics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "error": self.error.to_dict(),
            "fix": self.fix.to_dict() if self.fix else None,
            "context": {
                "file_content": self.context.file_content,
                "line_content": self.context.line_content,
                "line_number": self.context.line_number,
                "function_name": self.context.function_name,
                "class_name": self.context.class_name,
                "imports": self.context.imports,
                "variables": self.context.variables,
                "related_files": self.context.related_files,
                "dependencies": self.context.dependencies,
            },
            "timestamp": self.timestamp.isoformat(),
            "report_type": self.report_type,
            "status": self.status,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorReport":
        """Create report from dictionary."""
        error_data = data["error"]
        error = ErrorModel(
            id=error_data["id"],
            error_type=error_data["error_type"],
            message=error_data["message"],
            file_path=error_data["file_path"],
            line_number=error_data["line_number"],
            column=error_data.get("column"),
            severity=error_data["severity"],
            status=error_data["status"],
            traceback=error_data.get("traceback"),
            fix_attempts=error_data.get("fix_attempts", 0),
            max_retries=error_data.get("max_retries", 3),
            created_at=(
                datetime.fromisoformat(error_data["created_at"])
                if error_data.get("created_at")
                else None
            ),
        )

        fix_data = data.get("fix")
        fix = None
        if fix_data:
            fix = ErrorFix(
                error_id=fix_data["error_id"],
                success=fix_data["success"],
                message=fix_data["message"],
                changes=fix_data["changes"],
                fix_type=fix_data["fix_type"],
                backup_path=fix_data.get("backup_path"),
                fixed_at=(
                    datetime.fromisoformat(fix_data["fixed_at"])
                    if fix_data.get("fixed_at")
                    else None
                ),
            )

        context_data = data["context"]
        context = ErrorContext(
            file_content=context_data["file_content"],
            line_content=context_data["line_content"],
            line_number=context_data["line_number"],
            function_name=context_data.get("function_name"),
            class_name=context_data.get("class_name"),
            imports=context_data["imports"],
            variables=context_data["variables"],
            related_files=context_data["related_files"],
            dependencies=context_data["dependencies"],
        )

        return cls(
            error=error,
            fix=fix,
            context=context,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            report_type=data["report_type"],
            status=data["status"],
            metrics=data.get("metrics"),
            recommendations=data.get("recommendations"),
        )


@dataclass
class ErrorTask:
    """Error fix task."""

    id: str
    error_type: str
    message: str
    file_path: str
    line_number: int
    severity: str = ErrorSeverity.HIGH.value
    status: str = ErrorStatus.PENDING.value
    column: Optional[int] = None
    context: Dict[str, Any] = None
    traceback: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    fixed_at: Optional[datetime] = None
    fix: Optional[ErrorFix] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "error_type": self.error_type,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "severity": self.severity,
            "status": self.status,
            "context": self.context or {},
            "traceback": self.traceback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None,
            "fix": self.fix.to_dict() if self.fix else None,
        }


@dataclass
class AgentMetrics:
    """Agent metrics."""

    agent_id: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    success_rate: float
    errors_fixed: int
    tasks_completed: int
    tasks_pending: int
    uptime: float


@dataclass
class AgentActivity:
    """Agent activity information."""

    agent_id: str
    activity_type: str
    timestamp: datetime
    details: Dict[str, Any]
    status: str
    duration: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary."""
        return {
            "agent_id": self.agent_id,
            "activity_type": self.activity_type,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "status": self.status,
            "duration": self.duration,
            "error": self.error,
        }
