"""Project management and scanning page."""

from datetime import datetime
from pathlib import Path

import streamlit as st

from src.dashboard.state.agent_state import (
    assign_task,
    get_agent_status,
    initialize_session_state,
)
from src.error_management.models import ErrorSeverity


def scan_directory(directory: Path) -> dict:
    """Scan directory for files."""
    stats = {
        "total_files": 0,
        "python_files": 0,
        "yaml_files": 0,
        "json_files": 0,
        "other_files": 0,
        "directories": 0,
        "file_types": set(),
    }

    try:
        for item in directory.rglob("*"):
            if item.is_file():
                stats["total_files"] += 1
                ext = item.suffix.lower()
                stats["file_types"].add(ext)

                if ext == ".py":
                    stats["python_files"] += 1
                elif ext == ".yaml" or ext == ".yml":
                    stats["yaml_files"] += 1
                elif ext == ".json":
                    stats["json_files"] += 1
                else:
                    stats["other_files"] += 1
            elif item.is_dir():
                stats["directories"] += 1
    except Exception as e:
        st.error(f"Error scanning directory: {str(e)}")

    return stats


def main():
    """Main projects page."""
    st.title("Project Management")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Get agent status
    agent_status = get_agent_status()
    if not agent_status:
        st.warning("No agent is currently running")
        st.markdown("Create an agent from the home page to get started.")
        return

    # Project Selection
    st.subheader("Project Selection")

    # Get current directory
    current_dir = Path.cwd()
    parent_dir = current_dir.parent

    # Create directory selector
    col1, col2 = st.columns([3, 1])

    with col1:
        selected_dir = st.text_input("Project Directory", value=str(current_dir))

    with col2:
        if st.button("Browse Parent"):
            selected_dir = str(parent_dir)

    # Validate directory
    try:
        project_dir = Path(selected_dir)
        if not project_dir.exists():
            st.error("Directory does not exist")
            return
        if not project_dir.is_dir():
            st.error("Selected path is not a directory")
            return
    except Exception as e:
        st.error(f"Invalid directory path: {str(e)}")
        return

    # Project Analysis
    st.subheader("Project Analysis")

    # Scan directory
    stats = scan_directory(project_dir)

    # Display statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Files", stats["total_files"])
        st.metric("Directories", stats["directories"])

    with col2:
        st.metric("Python Files", stats["python_files"])
        st.metric("YAML Files", stats["yaml_files"])

    with col3:
        st.metric("JSON Files", stats["json_files"])
        st.metric("Other Files", stats["other_files"])

    with col4:
        st.metric("File Types", len(stats["file_types"]))
        file_types = ", ".join(sorted(stats["file_types"]))
        st.markdown(f"**Extensions:** {file_types}")

    # Scan Options
    st.subheader("Scan Options")

    col1, col2 = st.columns(2)

    with col1:
        scan_type = st.selectbox(
            "Scan Type", ["Full Scan", "Quick Scan", "Custom Scan"]
        )

        if scan_type == "Custom Scan":
            file_patterns = st.text_area("File Patterns", value="*.py\n*.yaml\n*.json")

            ignore_patterns = st.text_area(
                "Ignore Patterns", value="__pycache__\n*.pyc\nvenv\n.git"
            )

    with col2:
        severity_threshold = st.selectbox(
            "Minimum Severity", [s.value for s in ErrorSeverity]
        )

        auto_fix = st.toggle("Auto-fix Issues", value=True)
        backup_files = st.toggle("Backup Files", value=True)

    # Scan Controls
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Scan", type="primary"):
            # Create scan task
            task = {
                "id": f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "Project Scan",
                "priority": "High",
                "config": {
                    "directory": str(project_dir),
                    "scan_type": scan_type.lower().replace(" ", "_"),
                    "severity_threshold": severity_threshold,
                    "auto_fix": auto_fix,
                    "backup_files": backup_files,
                },
            }

            if scan_type == "Custom Scan":
                task["config"].update(
                    {
                        "file_patterns": file_patterns.split("\n"),
                        "ignore_patterns": ignore_patterns.split("\n"),
                    }
                )

            if assign_task(task):
                st.success("Scan task assigned successfully")
            else:
                st.error("Failed to assign scan task")

    with col2:
        if st.button("Schedule Scan"):
            st.info("Scan scheduling coming soon!")

    # Recent Scans
    st.subheader("Recent Scans")

    tasks = agent_status.get("tasks", [])
    scan_tasks = [t for t in tasks if t["type"] == "Project Scan"][-5:]

    if scan_tasks:
        for task in scan_tasks:
            with st.expander(f"Scan {task['id']}"):
                # Task details
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Status:** {task['status'].title()}")
                    st.markdown(f"**Directory:** {task['config']['directory']}")
                    st.markdown(f"**Type:** {task['config']['scan_type']}")

                with col2:
                    if "started_at" in task:
                        st.markdown(
                            f"**Started:** {task['started_at'].strftime('%H:%M:%S')}"
                        )
                    if "completed_at" in task:
                        st.markdown(
                            f"**Completed:** {task['completed_at'].strftime('%H:%M:%S')}"
                        )
                    if "duration" in task:
                        st.markdown(f"**Duration:** {task['duration']:.2f}s")

                # Scan results
                if "results" in task:
                    st.markdown("### Results")
                    results = task["results"]

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Files Scanned", results.get("files_scanned", 0))
                        st.metric("Issues Found", results.get("issues_found", 0))

                    with col2:
                        st.metric("Issues Fixed", results.get("issues_fixed", 0))
                        st.metric("Issues Failed", results.get("issues_failed", 0))

                    with col3:
                        st.metric(
                            "Critical Issues",
                            len(
                                [
                                    i
                                    for i in results.get("issues", [])
                                    if i["severity"] == ErrorSeverity.CRITICAL.value
                                ]
                            ),
                        )
                        st.metric(
                            "High Issues",
                            len(
                                [
                                    i
                                    for i in results.get("issues", [])
                                    if i["severity"] == ErrorSeverity.HIGH.value
                                ]
                            ),
                        )

                    # Progress bar
                    if results.get("files_scanned", 0) > 0:
                        progress = results.get("current_file", 0) / results.get(
                            "files_scanned", 1
                        )
                        st.progress(progress, f"Scan Progress: {progress * 100:.1f}%")
    else:
        st.info("No recent scans available")


if __name__ == "__main__":
    main()
