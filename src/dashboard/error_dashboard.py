"""Error Management System Dashboard."""

import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.error_management.autonomous_agent import autonomous_agent
from src.error_management.error_manager import ErrorManager

# Initialize managers
error_manager = ErrorManager()
executor = ThreadPoolExecutor()


def init_session_state():
    """Initialize session state variables."""
    if "agent_running" not in st.session_state:
        st.session_state.agent_running = False
    if "agent_task" not in st.session_state:
        st.session_state.agent_task = None
    if "last_agent_check" not in st.session_state:
        st.session_state.last_agent_check = None
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = "Stopped"


async def start_agent_async():
    """Start agent asynchronously."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    await autonomous_agent.initialize(api_key)
    await autonomous_agent.start()


async def stop_agent_async():
    """Stop agent asynchronously."""
    await autonomous_agent.stop()


def run_async(coro):
    """Run coroutine in the default event loop."""
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


async def check_agent_status():
    """Check actual agent status."""
    try:
        is_running = autonomous_agent.is_running
        current_task = autonomous_agent.current_task

        st.session_state.agent_running = is_running
        st.session_state.agent_status = "Running" if is_running else "Stopped"
        st.session_state.last_agent_check = datetime.now()

        return is_running, current_task
    except Exception as e:
        logging.error(f"Failed to check agent status: {str(e)}")
        return False, None


def display_agent_control():
    """Display agent control section with consistent status."""
    st.subheader("Agent Control")
    col1, col2 = st.columns(2)

    # Check agent status every 5 seconds
    if (
        not st.session_state.last_agent_check
        or (datetime.now() - st.session_state.last_agent_check).total_seconds() > 5
    ):
        is_running, current_task = run_async(check_agent_status())

    with col1:
        if not st.session_state.agent_running:
            if st.button("Start Agent"):
                try:
                    future = executor.submit(run_async, start_agent_async())
                    st.session_state.agent_task = future
                    st.session_state.agent_running = True
                    st.session_state.agent_status = "Running"
                    st.success("Agent started successfully")
                except Exception as e:
                    st.error(f"Failed to start agent: {str(e)}")
        else:
            if st.button("Stop Agent"):
                try:
                    future = executor.submit(run_async, stop_agent_async())
                    st.session_state.agent_task = future
                    st.session_state.agent_running = False
                    st.session_state.agent_status = "Stopped"
                    st.success("Agent stopped successfully")
                except Exception as e:
                    st.error(f"Failed to stop agent: {str(e)}")

    with col2:
        st.metric("Agent Status", st.session_state.agent_status)


def main():
    st.title("Error Management System Dashboard")
    init_session_state()

    # Display agent control with consistent status
    display_agent_control()

    # Create tabs for different sections
    tabs = st.tabs(["Metrics", "Errors", "Tasks", "Logs"])

    with tabs[0]:
        display_metrics()

    with tabs[1]:
        display_errors()

    with tabs[2]:
        display_tasks()

    with tabs[3]:
        display_logs()


def display_metrics():
    st.subheader("System Metrics")

    # Get error statistics
    stats = error_manager.get_error_stats()

    # Add loading state
    with st.spinner("Loading metrics..."):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Issues", stats.get("total_issues", 0))
        with col2:
            st.metric("Active Files", len(stats.get("issues_by_file", {})))
        with col3:
            last_update = stats.get("timestamp", datetime.now().isoformat())
            if isinstance(last_update, str):
                last_update = last_update.split("T")[1].split(".")[0]
            st.metric("Last Update", last_update)

        # Create trend graph with error handling
        try:
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=7), end=datetime.now(), freq="D"
            )
            values = [0] * len(dates)  # Default to zeros

            if stats.get("issues_by_date"):
                for date, count in stats["issues_by_date"].items():
                    try:
                        idx = dates.get_loc(pd.to_datetime(date))
                        values[idx] = count
                    except KeyError:
                        continue

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=dates, y=values, mode="lines+markers", name="Issues")
            )
            fig.update_layout(
                title="Issue Trend (Last 7 Days)",
                xaxis_title="Date",
                yaxis_title="Number of Issues",
            )
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Failed to create trend graph: {str(e)}")


def display_errors():
    st.subheader("Recent Issues")

    # Get current issues
    issues = error_manager.get_issues()

    if issues:
        for issue in issues:
            with st.expander(f"Issues in {issue['file']}"):
                for i in issue["issues"]:
                    st.write(f"- {i}")
    else:
        st.info("No active issues found")


def display_tasks():
    st.subheader("Task Queue")

    # Get tasks with error handling
    try:
        tasks = run_async(task_manager.get_pending_tasks())
        all_tasks = task_manager.tasks  # Get all tasks for history

        if tasks or all_tasks:
            # Show active tasks
            st.subheader("Active Tasks")
            active_df = pd.DataFrame(
                [t for t in all_tasks if t["status"] in ["pending", "in_progress"]]
            )
            if not active_df.empty:
                st.dataframe(active_df)
            else:
                st.info("No active tasks")

            # Show task history
            st.subheader("Task History")
            history_df = pd.DataFrame(
                [t for t in all_tasks if t["status"] in ["completed", "failed"]]
            )
            if not history_df.empty:
                st.dataframe(history_df)
            else:
                st.info("No task history")
        else:
            st.info("No tasks found")

    except Exception as e:
        st.error(f"Failed to load tasks: {str(e)}")


def display_logs():
    st.subheader("System Logs")

    try:
        log_file = Path("logs/autonomous_agent.log")
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = f.readlines()[-50:]  # Last 50 lines
                st.text_area("Recent Logs", value="".join(logs), height=300)
        else:
            st.warning("Log file not found")
    except Exception as e:
        st.error(f"Failed to read logs: {str(e)}")


if __name__ == "__main__":
    main()
