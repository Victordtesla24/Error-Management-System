"""Agents management page."""

import streamlit as st

from src.dashboard.components.agents import (
    display_agent_controls,
    display_agent_metrics,
    display_agent_status,
    display_agent_tasks,
)
from src.dashboard.state.agent_state import (
    get_agent_logs,
    get_agent_metrics,
    get_agent_status,
    get_agent_tasks,
    get_error_stats,
    get_performance_stats,
    initialize_session_state,
)


def main():
    """Main agents page."""
    st.title("Agent Management")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Get agent status
    agent_status = get_agent_status()
    if not agent_status:
        st.warning("No agent is currently running")
        st.markdown("Create an agent from the home page to get started.")
        return

    # Layout
    col1, col2 = st.columns([2, 1])

    # Agent Status and Controls
    with col1:
        display_agent_status(agent_status)
        st.markdown("---")
        display_agent_controls(agent_status)

    # Agent Metrics
    with col2:
        display_agent_metrics(get_agent_metrics())

    st.markdown("---")

    # Tasks and Logs
    tab1, tab2, tab3 = st.tabs(["Tasks", "Logs", "Statistics"])

    # Tasks Tab
    with tab1:
        display_agent_tasks(get_agent_tasks())

    # Logs Tab
    with tab2:
        logs = get_agent_logs()
        if logs:
            for log in logs:
                timestamp = log["timestamp"].strftime("%H:%M:%S")
                level_color = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🟢"}.get(
                    log["level"], "⚪"
                )

                st.markdown(
                    f"{timestamp} - {level_color} **{log['level']}**: {log['message']}"
                )
        else:
            st.info("No logs available")

    # Statistics Tab
    with tab3:
        col1, col2 = st.columns(2)

        # Error Statistics
        with col1:
            st.subheader("Error Statistics")
            error_stats = get_error_stats()

            # Create metrics
            col11, col12 = st.columns(2)
            with col11:
                st.metric("Total Errors", error_stats["total"])
                st.metric("Fixed", error_stats["fixed"])
                st.metric("Failed", error_stats["failed"])
            with col12:
                st.metric("Critical", error_stats["critical"])
                st.metric("High", error_stats["high"])
                st.metric("Medium", error_stats["medium"])

            # Create progress bar
            if error_stats["total"] > 0:
                fixed_percent = (error_stats["fixed"] / error_stats["total"]) * 100
                st.progress(fixed_percent / 100, f"Fix Rate: {fixed_percent:.1f}%")

        # Performance Statistics
        with col2:
            st.subheader("Performance Statistics")
            perf_stats = get_performance_stats()

            # Create metrics
            col21, col22 = st.columns(2)
            with col21:
                cpu_usage = perf_stats.get("cpu_usage", 0)
                cpu_color = "🟢" if cpu_usage < 70 else "🟡" if cpu_usage < 90 else "🔴"
                st.markdown(f"CPU Usage: {cpu_color} {cpu_usage:.1f}%")

                memory_usage = perf_stats.get("memory_usage", 0)
                memory_color = (
                    "🟢" if memory_usage < 70 else "🟡" if memory_usage < 90 else "🔴"
                )
                st.markdown(f"Memory Usage: {memory_color} {memory_usage:.1f}%")

            with col22:
                response_time = perf_stats.get("response_time", 0)
                response_color = (
                    "🟢"
                    if response_time < 0.5
                    else "🟡" if response_time < 1.0 else "🔴"
                )
                st.markdown(f"Response Time: {response_color} {response_time:.3f}s")

                success_rate = perf_stats.get("success_rate", 0)
                success_color = (
                    "🟢" if success_rate > 90 else "🟡" if success_rate > 70 else "🔴"
                )
                st.markdown(f"Success Rate: {success_color} {success_rate:.1f}%")

            # Create progress bars
            st.progress(cpu_usage / 100, "CPU Usage")
            st.progress(memory_usage / 100, "Memory Usage")
            st.progress(success_rate / 100, "Success Rate")


if __name__ == "__main__":
    main()
