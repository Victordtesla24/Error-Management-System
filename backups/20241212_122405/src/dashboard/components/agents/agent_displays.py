"""Agent display components."""

import streamlit as st

from src.dashboard.state.agent_state import assign_task, start_agent, stop_agent
from src.error_management.models import ErrorSeverity, ErrorStatus


def display_agent_status(agent_status: dict) -> None:
    """Display agent status."""
    if not agent_status:
        return

    # Status header
    status_color = {"running": "🟢", "stopped": "🔴", "error": "🟡"}.get(
        agent_status["status"], "⚪"
    )

    st.markdown(f"### Agent Status {status_color}")

    # Status details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Name:** {agent_status['name']}")
        st.markdown(f"**Type:** {agent_status['type']}")
        st.markdown(
            f"**Created:** {agent_status['created_at'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

    with col2:
        st.markdown(f"**Status:** {agent_status['status'].title()}")
        if agent_status["status"] == "running":
            if st.button("Stop Agent"):
                if stop_agent():
                    st.success("Agent stopped successfully")
                    st.rerun()
                else:
                    st.error("Failed to stop agent")
        else:
            if st.button("Start Agent"):
                if start_agent():
                    st.success("Agent started successfully")
                    st.rerun()
                else:
                    st.error("Failed to start agent")


def display_agent_metrics(metrics) -> None:
    """Display agent metrics."""
    if not metrics:
        return

    st.markdown("### Agent Metrics")

    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)

    # Resource metrics
    with col1:
        cpu_usage = metrics.cpu_usage
        cpu_color = "🟢" if cpu_usage < 70 else "🟡" if cpu_usage < 90 else "🔴"
        st.metric(
            "CPU Usage",
            f"{cpu_usage:.1f}%",
            delta=f"{cpu_usage - 70:.1f}%" if cpu_usage > 70 else None,
            delta_color="inverse",
        )
        st.markdown(f"Status: {cpu_color}")

    with col2:
        memory_usage = metrics.memory_usage
        memory_color = (
            "🟢" if memory_usage < 70 else "🟡" if memory_usage < 90 else "🔴"
        )
        st.metric(
            "Memory Usage",
            f"{memory_usage:.1f}%",
            delta=f"{memory_usage - 70:.1f}%" if memory_usage > 70 else None,
            delta_color="inverse",
        )
        st.markdown(f"Status: {memory_color}")

    # Performance metrics
    with col3:
        response_time = metrics.response_time
        response_color = (
            "🟢" if response_time < 0.5 else "🟡" if response_time < 1.0 else "🔴"
        )
        st.metric(
            "Response Time",
            f"{response_time:.3f}s",
            delta=f"{response_time - 0.5:.3f}s" if response_time > 0.5 else None,
            delta_color="inverse",
        )
        st.markdown(f"Status: {response_color}")

    with col4:
        success_rate = metrics.success_rate
        success_color = (
            "🟢" if success_rate > 90 else "🟡" if success_rate > 70 else "🔴"
        )
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=f"{success_rate - 90:.1f}%" if success_rate < 90 else None,
            delta_color="normal",
        )
        st.markdown(f"Status: {success_color}")

    # Progress bars
    col1, col2 = st.columns(2)

    with col1:
        st.progress(cpu_usage / 100, "CPU Usage")
        st.progress(memory_usage / 100, "Memory Usage")

    with col2:
        st.progress(min(response_time, 2) / 2, "Response Time")
        st.progress(success_rate / 100, "Success Rate")


def display_agent_controls() -> None:
    """Display agent controls."""
    st.markdown("### Agent Controls")

    # Create control columns
    col1, col2 = st.columns(2)

    with col1:
        # Task creation
        task_type = st.selectbox(
            "Task Type", ["Run Tests", "Fix Errors", "Code Analysis"]
        )

        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

    with col2:
        # Task configuration
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

    # Submit button
    if st.button("Create Task"):
        # Create task
        task = {
            "type": task_type,
            "priority": priority,
            "config": config,
            "status": "pending",  # Set initial status
        }

        if assign_task(task):
            st.success("Task created successfully")
            st.rerun()
        else:
            st.error("Failed to create task")


def display_agent_tasks(tasks: list) -> None:
    """Display agent tasks."""
    if not tasks:
        st.info("No tasks available")
        return

    st.markdown("### Agent Tasks")

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
        filtered_tasks = [t for t in filtered_tasks if t.get("status") == task_status]

    # Display tasks
    for task in filtered_tasks:
        with st.expander(f"{task['type']} - {task.get('id', 'Unknown')}"):
            # Task details
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Status:** {task.get('status', 'pending').title()}")
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
