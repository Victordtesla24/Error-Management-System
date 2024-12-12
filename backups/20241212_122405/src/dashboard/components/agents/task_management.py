"""Agent task management components."""

from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from src.dashboard.state.agent_state import assign_task
from src.error_management.models import ErrorSeverity, ErrorStatus


def display_task_list(tasks: List[Dict[str, Any]]) -> None:
    """Display list of tasks."""
    if not tasks:
        st.info("No tasks available")
        return

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        task_type = st.selectbox(
            "Filter by Type", ["All"] + list(set(t["type"] for t in tasks))
        )
    with col2:
        task_status = st.selectbox(
            "Filter by Status", ["All", "pending", "running", "completed", "failed"]
        )

    # Filter tasks
    filtered_tasks = tasks
    if task_type != "All":
        filtered_tasks = [t for t in filtered_tasks if t["type"] == task_type]
    if task_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t["status"] == task_status]

    # Display tasks
    for task in filtered_tasks:
        with st.expander(f"{task['type']} - {task['id']}"):
            # Task details
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Status:** {task['status'].title()}")
                if "started_at" in task:
                    st.markdown(
                        f"**Started:** {task['started_at'].strftime('%H:%M:%S')}"
                    )

            with col2:
                st.markdown(f"**Priority:** {task.get('priority', 'Medium')}")
                if "completed_at" in task:
                    st.markdown(
                        f"**Completed:** {task['completed_at'].strftime('%H:%M:%S')}"
                    )

            with col3:
                if "duration" in task:
                    st.markdown(f"**Duration:** {task['duration']:.2f}s")

            # Error details if present
            if "error" in task:
                st.markdown("#### Error Details")
                error = task["error"]

                # Error message and location
                st.markdown(f"**Message:** {error.get('message', 'Unknown error')}")
                st.markdown(f"**File:** {error.get('file_path', 'Unknown file')}")
                st.markdown(f"**Line:** {error.get('line_number', 'Unknown')}")

                # Error severity and status
                severity = error.get("severity", ErrorSeverity.HIGH.value)
                severity_color = {
                    ErrorSeverity.CRITICAL.value: "🔴",
                    ErrorSeverity.HIGH.value: "🟡",
                    ErrorSeverity.MEDIUM.value: "🟢",
                    ErrorSeverity.LOW.value: "⚪",
                }.get(severity, "⚪")

                status = error.get("status", ErrorStatus.PENDING.value)
                status_color = {
                    ErrorStatus.FIXED.value: "🟢",
                    ErrorStatus.FAILED.value: "🔴",
                    ErrorStatus.FIXING.value: "🟡",
                    ErrorStatus.PENDING.value: "⚪",
                }.get(status, "⚪")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Severity:** {severity_color} {severity}")
                with col2:
                    st.markdown(f"**Status:** {status_color} {status}")

                # Fix details if present
                if "fix" in error:
                    st.markdown("#### Fix Details")
                    fix = error["fix"]
                    st.markdown(f"**Type:** {fix['fix_type']}")
                    st.markdown(f"**Success:** {'✅' if fix['success'] else '❌'}")
                    if fix.get("changes"):
                        st.markdown("**Changes:**")
                        for change in fix["changes"]:
                            st.code(
                                f"- {change['type']}: "
                                f"{change.get('old', '')} -> {change.get('new', '')}"
                            )

            # Task results if present
            if "results" in task:
                st.markdown("#### Results")
                results = task["results"]

                if task["type"] == "Run Tests":
                    st.markdown("**Test Summary:**")
                    summary = results.get("test_summary", {})
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"Total: {summary.get('total', 0)}")
                        st.markdown(f"Passed: {summary.get('passed', 0)}")
                        st.markdown(f"Failed: {summary.get('failed', 0)}")
                    with col2:
                        st.markdown(f"Errors: {summary.get('errors', 0)}")
                        st.markdown(f"Skipped: {summary.get('skipped', 0)}")
                        st.markdown(f"Coverage: {summary.get('coverage', 0):.1f}%")
                else:
                    st.json(results)


def create_task_form() -> None:
    """Display task creation form."""
    st.subheader("Create Task")

    with st.form("create_task"):
        # Task type
        task_type = st.selectbox(
            "Task Type", ["Run Tests", "Fix Errors", "Code Analysis", "Project Scan"]
        )

        # Task priority
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

        # Task config
        st.markdown("### Task Configuration")

        if task_type == "Run Tests":
            test_pattern = st.text_input("Test Pattern", value="test_*.py")
            parallel = st.checkbox("Run in Parallel", value=True)
            config = {"test_pattern": test_pattern, "parallel": parallel}

        elif task_type == "Fix Errors":
            auto_fix = st.checkbox("Auto Fix", value=True)
            backup = st.checkbox("Create Backup", value=True)
            config = {"auto_fix": auto_fix, "backup": backup}

        elif task_type == "Code Analysis":
            file_pattern = st.text_input("File Pattern", value="*.py")
            ignore_pattern = st.text_input(
                "Ignore Pattern", value="__pycache__,*.pyc,venv,.git"
            )
            config = {
                "file_pattern": file_pattern,
                "ignore_pattern": ignore_pattern.split(","),
            }

        elif task_type == "Project Scan":
            scan_type = st.selectbox(
                "Scan Type", ["Full Scan", "Quick Scan", "Custom Scan"]
            )
            severity_threshold = st.selectbox(
                "Minimum Severity", [s.value for s in ErrorSeverity]
            )
            config = {
                "scan_type": scan_type.lower().replace(" ", "_"),
                "severity_threshold": severity_threshold,
            }

        # Submit button
        if st.form_submit_button("Create Task"):
            # Create task
            task = {
                "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": task_type,
                "priority": priority,
                "config": config,
            }

            if assign_task(task):
                st.success("Task created successfully")
            else:
                st.error("Failed to create task")
