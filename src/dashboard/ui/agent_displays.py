"""Agent display components."""

from datetime import datetime
from typing import Any, Dict

import streamlit as st

from src.dashboard.components.agents import agent_configuration_form
from src.dashboard.state import (
    get_agent_activities,
    get_agent_container,
    get_agent_logs,
    get_agent_metrics,
    get_agent_security,
    start_agent,
    stop_agent,
)


def display_agent_details(agent: Dict[str, Any]) -> None:
    """Display agent details and controls."""
    try:
        # Agent Controls
        st.subheader("🤖 Agent Controls")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**Name:** {agent['name']}")
            st.write(f"**Type:** {agent['type']}")
            st.write(f"**Status:** {agent['status']}")
        with col2:
            if agent["status"] in ["idle", "stopped", "error"]:
                if st.button("▶️ Start Agent", type="primary", use_container_width=True):
                    start_agent(agent["id"])
            elif agent["status"] == "running":
                if st.button(
                    "⏹️ Stop Agent", type="secondary", use_container_width=True
                ):
                    stop_agent(agent["id"])
        with col3:
            if st.button("⚙️ Configure", use_container_width=True):
                st.session_state.show_config = True

        # Configuration Form
        if st.session_state.get("show_config", False):
            st.divider()
            st.subheader("⚙️ Agent Configuration")
            if agent_configuration_form(agent):
                st.session_state.show_config = False

        # Real-time Performance
        st.divider()
        st.subheader("📊 Real-time Performance")
        metrics = get_agent_metrics(agent["id"])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "CPU Usage",
                f"{metrics.get('cpu_usage', 0):.1f}%",
                delta=f"{metrics.get('cpu_usage_delta', 0):.1f}%",
            )
        with col2:
            st.metric(
                "Memory Usage",
                f"{metrics.get('memory_usage', 0):.1f}%",
                delta=f"{metrics.get('memory_usage_delta', 0):.1f}%",
            )
        with col3:
            st.metric(
                "Response Time",
                f"{metrics.get('response_time', 0):.3f}ms",
                delta=f"{metrics.get('response_time_delta', 0):.3f}ms",
            )
        with col4:
            st.metric(
                "Success Rate",
                f"{metrics.get('success_rate', 100):.1f}%",
                delta=f"{metrics.get('success_rate_delta', 0):.1f}%",
            )

        # Task Performance
        st.divider()
        st.subheader("📈 Task Performance")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Errors Fixed", metrics.get("errors_fixed", 0))
        with col2:
            st.metric("Active Time", f"{metrics.get('active_time', 0)}h")
        with col3:
            st.metric("Tasks Completed", metrics.get("tasks_completed", 0))
        with col4:
            st.metric("Tasks Pending", metrics.get("tasks_pending", 0))

        # Security Status
        st.divider()
        st.subheader("🔒 Security Status")
        security = get_agent_security(agent["id"])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Security Score", f"{security.get('score', 100)}/100")
        with col2:
            st.metric("Vulnerabilities", security.get("vulnerabilities", 0))
        with col3:
            last_scan = security.get("last_scan", datetime.now())
            st.metric("Last Scan", last_scan.strftime("%H:%M:%S"))

        # Container Details
        st.divider()
        st.subheader("📦 Container Details")
        container = get_agent_container(agent["id"])
        if container:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Status:** {container.get('status', 'unknown')}")
                st.write(f"**Image:** {container.get('image', 'N/A')}")
            with col2:
                st.write("**Ports:**")
                for port in container.get("ports", {}).items():
                    st.write(f"- {port[0]}: {port[1]}")
            with col3:
                st.write("**Resources:**")
                resources = container.get("resources", {})
                st.write(f"- CPU: {resources.get('cpu_limit', 'N/A')}")
                st.write(f"- Memory: {resources.get('memory_limit', 'N/A')}")
                st.write(f"- Storage: {resources.get('storage_limit', 'N/A')}")

        # Activity Log
        st.divider()
        st.subheader("📝 Activity Log")
        activities = get_agent_activities(agent["id"])
        if activities:
            for activity in activities[:5]:  # Show last 5 activities
                with st.expander(
                    f"{activity['timestamp'].strftime('%H:%M:%S')} - {activity['type']}",
                    expanded=False,
                ):
                    st.write(f"**Status:** {activity['status']}")
                    st.write(f"**Details:** {activity['details']}")
        else:
            st.info("No activities recorded")

        # Error Log
        st.divider()
        st.subheader("⚠️ Error Log")
        logs = get_agent_logs(agent["id"])
        error_logs = [log for log in logs if log["level"] == "ERROR"]
        if error_logs:
            for log in error_logs[:5]:  # Show last 5 errors
                with st.expander(
                    f"{log['timestamp'].strftime('%H:%M:%S')} - Error", expanded=False
                ):
                    st.error(log["message"])
        else:
            st.success("No errors reported")

    except Exception as e:
        st.error(f"Error displaying agent details: {str(e)}")
        import traceback

        st.error(traceback.format_exc())
