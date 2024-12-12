"""Dashboard home page."""

import streamlit as st

from src.dashboard.components.agents.agent_creation import display_agent_creation_form
from src.dashboard.state.agent_state import (
    get_agent_metrics,
    get_agent_status,
    initialize_session_state,
)
from src.error_management.models import ErrorSeverity, ErrorStatus


def main():
    """Main dashboard page."""
    st.set_page_config(
        page_title="Error Management System", page_icon="🔧", layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("Error Management System")
    st.markdown("---")

    # Get agent status
    agent_status = get_agent_status()

    if not agent_status:
        # No agent running - show creation form
        st.warning("No agent is currently running")
        display_agent_creation_form()
        return

    # System Status
    col1, col2, col3 = st.columns(3)

    # Agent Status
    with col1:
        st.subheader("Agent Status")
        status_color = {"running": "🟢", "stopped": "🔴", "error": "🟡"}.get(
            agent_status["status"], "⚪"
        )

        st.markdown(f"Status: {status_color} {agent_status['status'].title()}")
        st.markdown(f"Type: {agent_status['type']}")
        st.markdown(
            f"Created: {agent_status['created_at'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # Error Statistics
    with col2:
        st.subheader("Error Statistics")
        metrics = get_agent_metrics()

        # Create metrics
        col21, col22 = st.columns(2)
        with col21:
            st.metric("Errors Fixed", metrics.errors_fixed if metrics else 0)
            st.metric(
                "Success Rate", f"{metrics.success_rate:.1f}%" if metrics else "0.0%"
            )
        with col22:
            st.metric("Tasks Completed", metrics.tasks_completed if metrics else 0)
            st.metric("Tasks Pending", metrics.tasks_pending if metrics else 0)

    # System Health
    with col3:
        st.subheader("System Health")

        # Create health metrics
        col31, col32 = st.columns(2)
        with col31:
            cpu_usage = metrics.cpu_usage if metrics else 0.0
            cpu_color = "🟢" if cpu_usage < 70 else "🟡" if cpu_usage < 90 else "🔴"
            st.markdown(f"CPU Usage: {cpu_color} {cpu_usage:.1f}%")

            memory_usage = metrics.memory_usage if metrics else 0.0
            memory_color = (
                "🟢" if memory_usage < 70 else "🟡" if memory_usage < 90 else "🔴"
            )
            st.markdown(f"Memory Usage: {memory_color} {memory_usage:.1f}%")

        with col32:
            response_time = metrics.response_time if metrics else 0.0
            response_color = (
                "🟢" if response_time < 0.5 else "🟡" if response_time < 1.0 else "🔴"
            )
            st.markdown(f"Response Time: {response_color} {response_time:.3f}s")

    st.markdown("---")

    # Recent Activity
    st.subheader("Recent Activity")
    activities = agent_status.get("activities", [])[-5:]  # Get last 5 activities

    if activities:
        for activity in activities:
            timestamp = activity["timestamp"].strftime("%H:%M:%S")
            status_color = {"Success": "🟢", "Error": "🔴", "Warning": "🟡"}.get(
                activity["status"], "⚪"
            )

            st.markdown(
                f"{timestamp} - {status_color} **{activity['type']}**: "
                f"{activity['details']}"
            )
    else:
        st.info("No recent activity")

    # Error List
    st.subheader("Recent Errors")
    tasks = agent_status.get("tasks", [])
    error_tasks = [t for t in tasks if t.get("type") == "Fix Errors"][-5:]

    if error_tasks:
        for task in error_tasks:
            error = task.get("error", {})
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.markdown(f"**{error.get('message', 'Unknown error')}**")
            with col2:
                severity = error.get("severity", ErrorSeverity.HIGH.value)
                severity_color = {
                    ErrorSeverity.CRITICAL.value: "🔴",
                    ErrorSeverity.HIGH.value: "🟡",
                    ErrorSeverity.MEDIUM.value: "🟢",
                    ErrorSeverity.LOW.value: "⚪",
                }.get(severity, "⚪")
                st.markdown(f"Severity: {severity_color} {severity}")
            with col3:
                status = error.get("status", ErrorStatus.PENDING.value)
                status_color = {
                    ErrorStatus.FIXED.value: "🟢",
                    ErrorStatus.FAILED.value: "🔴",
                    ErrorStatus.FIXING.value: "🟡",
                    ErrorStatus.PENDING.value: "⚪",
                }.get(status, "⚪")
                st.markdown(f"Status: {status_color} {status}")
            with col4:
                if status == ErrorStatus.PENDING.value:
                    if st.button("Fix Now", key=f"fix_{task['id']}"):
                        # Update task priority
                        task["priority"] = "Critical"
                        st.rerun()
    else:
        st.success("No recent errors")

    # Footer
    st.markdown("---")
    st.markdown("Error Management System - Autonomous error detection and fixing")


if __name__ == "__main__":
    main()
