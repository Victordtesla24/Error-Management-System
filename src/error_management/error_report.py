"""Error reporting module."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ErrorContext, ErrorFix, ErrorModel, ErrorReport, ErrorStatus


def generate_report(
    error: ErrorModel,
    fix: Optional[ErrorFix] = None,
    context: Optional[ErrorContext] = None,
) -> ErrorReport:
    """Generate error report."""
    try:
        # Create report
        report = ErrorReport(
            error=error,
            fix=fix,
            context=context
            or ErrorContext(file_content="", line_content="", line_number=0),
            timestamp=datetime.now(),
            report_type="error_fix",
            status=error.status,
        )

        # Save report
        save_report(report)

        return report

    except Exception as e:
        logging.error(f"Failed to generate report: {str(e)}")
        raise


def save_report(report: ErrorReport) -> None:
    """Save error report to file."""
    try:
        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Create report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_report_{timestamp}.md"
        report_path = reports_dir / filename

        # Generate markdown content
        content = generate_markdown_report(report)

        # Write report
        report_path.write_text(content)

        # Also save JSON version for processing
        json_path = reports_dir / f"error_report_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

    except Exception as e:
        logging.error(f"Failed to save report: {str(e)}")
        raise


def generate_markdown_report(report: ErrorReport) -> str:
    """Generate markdown formatted report."""
    try:
        content = [
            "# Error Report\n",
            f"## Overview\n",
            f"- **Timestamp:** {report.timestamp.isoformat()}",
            f"- **Type:** {report.error.type}",
            f"- **Status:** {report.error.status}",
            f"- **Severity:** {report.error.severity}\n",
            f"## Error Details\n",
            f"- **Message:** {report.error.message}",
            f"- **File:** {report.error.file_path}",
            f"- **Line:** {report.error.line_number}",
            f"- **Fix Attempts:** {report.error.fix_attempts}/{report.error.max_retries}\n",
        ]

        if report.error.traceback:
            content.extend(
                ["## Traceback\n", "```python", *report.error.traceback, "```\n"]
            )

        if report.context:
            content.extend(
                [
                    "## Context\n",
                    "### Code\n",
                    "```python",
                    report.context.line_content,
                    "```\n",
                    f"### Function: {report.context.function_name or 'N/A'}",
                    f"### Class: {report.context.class_name or 'N/A'}\n",
                ]
            )

            if report.context.imports:
                content.extend(
                    ["### Imports\n", "```python", *report.context.imports, "```\n"]
                )

        if report.fix:
            content.extend(
                [
                    "## Fix Details\n",
                    f"- **Type:** {report.fix.fix_type}",
                    f"- **Success:** {report.fix.success}",
                    f"- **Fixed At:** {report.fix.fixed_at.isoformat()}",
                    f"- **Backup:** {report.fix.backup_path or 'N/A'}\n",
                    "### Changes\n",
                ]
            )

            for change in report.fix.changes:
                content.extend(
                    [
                        f"#### {change['type'].title()}\n",
                        "```diff",
                        f"- {change.get('old', '')}",
                        f"+ {change.get('new', '')}",
                        "```\n",
                    ]
                )

        if report.metrics:
            content.extend(
                [
                    "## Metrics\n",
                    "```json",
                    json.dumps(report.metrics, indent=2),
                    "```\n",
                ]
            )

        if report.recommendations:
            content.extend(
                [
                    "## Recommendations\n",
                    *[f"- {rec}" for rec in report.recommendations],
                    "\n",
                ]
            )

        return "\n".join(content)

    except Exception as e:
        logging.error(f"Failed to generate markdown report: {str(e)}")
        raise


def get_recent_reports(limit: int = 10) -> List[ErrorReport]:
    """Get recent error reports."""
    try:
        reports_dir = Path("reports")
        if not reports_dir.exists():
            return []

        # Get JSON report files
        report_files = sorted(
            reports_dir.glob("error_report_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]

        reports = []
        for file in report_files:
            try:
                with open(file) as f:
                    data = json.load(f)
                reports.append(ErrorReport.from_dict(data))
            except Exception as e:
                logging.error(f"Failed to load report {file}: {str(e)}")
                continue

        return reports

    except Exception as e:
        logging.error(f"Failed to get recent reports: {str(e)}")
        return []


def analyze_reports(reports: List[ErrorReport]) -> Dict[str, Any]:
    """Analyze error reports for patterns."""
    try:
        analysis = {
            "total_errors": len(reports),
            "fixed_errors": len(
                [r for r in reports if r.error.status == ErrorStatus.FIXED.value]
            ),
            "failed_errors": len(
                [r for r in reports if r.error.status == ErrorStatus.FAILED.value]
            ),
            "error_types": {},
            "fix_types": {},
            "common_files": {},
            "avg_fix_time": 0,
            "success_rate": 0,
        }

        # Analyze error types
        for report in reports:
            # Count error types
            error_type = report.error.type
            analysis["error_types"][error_type] = (
                analysis["error_types"].get(error_type, 0) + 1
            )

            # Count fix types
            if report.fix:
                fix_type = report.fix.fix_type
                analysis["fix_types"][fix_type] = (
                    analysis["fix_types"].get(fix_type, 0) + 1
                )

            # Count affected files
            file_path = str(report.error.file_path)
            analysis["common_files"][file_path] = (
                analysis["common_files"].get(file_path, 0) + 1
            )

        # Calculate metrics
        if reports:
            # Calculate average fix time
            fix_times = []
            for report in reports:
                if report.fix and report.fix.fixed_at and report.error.created_at:
                    fix_time = (
                        report.fix.fixed_at - report.error.created_at
                    ).total_seconds()
                    fix_times.append(fix_time)
            if fix_times:
                analysis["avg_fix_time"] = sum(fix_times) / len(fix_times)

            # Calculate success rate
            analysis["success_rate"] = (
                analysis["fixed_errors"] / analysis["total_errors"]
            ) * 100

        return analysis

    except Exception as e:
        logging.error(f"Failed to analyze reports: {str(e)}")
        return {}
