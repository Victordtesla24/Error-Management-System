"""System monitoring and performance metrics page."""

import streamlit as st

from src.dashboard.state.agent_state import (
    get_agent_metrics,
    get_agent_status,
    get_performance_stats,
    initialize_session_state,
)


def main():
    """Main monitoring page."""
    st.title("System Monitoring")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Get agent status
    agent_status = get_agent_status()
    if not agent_status:
        st.warning("No agent is currently running")
        st.markdown("Create an agent from the home page to get started.")
        return

    # Current Metrics
    st.subheader("Current Metrics")
    metrics = get_agent_metrics()

    if metrics:
        # Create metric columns
        col1, col2, col3, col4 = st.columns(4)

        # CPU Usage
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

        # Memory Usage
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

        # Response Time
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

        # Success Rate
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

    st.markdown("---")

    # Metrics History
    st.subheader("Metrics History")

    # Get metrics history from session state
    metrics_history = st.session_state.metrics_history

    if metrics_history:
        # Create line charts
        col1, col2 = st.columns(2)

        with col1:
            # CPU and Memory Usage
            st.line_chart(
                {
                    "CPU Usage": [m["metrics"].cpu_usage for m in metrics_history],
                    "Memory Usage": [
                        m["metrics"].memory_usage for m in metrics_history
                    ],
                }
            )

        with col2:
            # Response Time and Success Rate
            st.line_chart(
                {
                    "Response Time": [
                        m["metrics"].response_time for m in metrics_history
                    ],
                    "Success Rate": [
                        m["metrics"].success_rate for m in metrics_history
                    ],
                }
            )
    else:
        st.info("No metrics history available")

    st.markdown("---")

    # Performance Analysis
    st.subheader("Performance Analysis")
    perf_stats = get_performance_stats()

    if perf_stats:
        # Create analysis columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Resource Usage")

            # CPU Analysis
            cpu_usage = perf_stats["cpu_usage"]
            st.markdown(
                f"**CPU Usage:** {cpu_usage:.1f}% "
                f"({'High' if cpu_usage > 70 else 'Normal'})"
            )

            # Memory Analysis
            memory_usage = perf_stats["memory_usage"]
            st.markdown(
                f"**Memory Usage:** {memory_usage:.1f}% "
                f"({'High' if memory_usage > 70 else 'Normal'})"
            )

        with col2:
            st.markdown("### Performance Metrics")

            # Response Time Analysis
            response_time = perf_stats["response_time"]
            st.markdown(
                f"**Response Time:** {response_time:.3f}s "
                f"({'Slow' if response_time > 0.5 else 'Fast'})"
            )

            # Success Rate Analysis
            success_rate = perf_stats["success_rate"]
            st.markdown(
                f"**Success Rate:** {success_rate:.1f}% "
                f"({'Good' if success_rate > 90 else 'Needs Improvement'})"
            )

        # Performance Recommendations
        st.markdown("### Recommendations")

        recommendations = []
        if cpu_usage > 70:
            recommendations.append("- Consider optimizing CPU-intensive operations")
        if memory_usage > 70:
            recommendations.append(
                "- Monitor memory usage and consider increasing limits"
            )
        if response_time > 0.5:
            recommendations.append(
                "- Investigate slow operations and optimize response times"
            )
        if success_rate < 90:
            recommendations.append(
                "- Review error patterns and implement fixes to improve success rate"
            )

        if recommendations:
            for rec in recommendations:
                st.markdown(rec)
        else:
            st.success("System is performing optimally")
    else:
        st.info("No performance statistics available")


if __name__ == "__main__":
    main()
