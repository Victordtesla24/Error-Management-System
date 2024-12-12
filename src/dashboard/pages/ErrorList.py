"""Error list and management page."""

import streamlit as st

from src.dashboard.state.agent_state import (
    assign_task,
    get_agent_status,
    get_error_stats,
    initialize_session_state,
)
from src.error_management.models import ErrorSeverity, ErrorStatus


def main():
    """Main error list page."""
    st.title("Error Management")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Get agent status
    agent_status = get_agent_status()
    if not agent_status:
        st.warning("No agent is currently running")
        st.markdown("Create an agent from the home page to get started.")
        return

    # Error Statistics
    st.subheader("Error Statistics")
    stats = get_error_stats()

    # Create metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Errors", stats["total"])
        st.metric("Fixed", stats["fixed"])

    with col2:
        st.metric("Pending", stats["pending"])
        st.metric("Failed", stats["failed"])

    with col3:
        st.metric("Critical", stats["critical"])
        st.metric("High", stats["high"])

    with col4:
        st.metric("Medium", stats["medium"])
        st.metric("Low", stats["low"])

    # Progress bars
    if stats["total"] > 0:
        col1, col2 = st.columns(2)

        with col1:
            # Fix progress
            fixed_percent = (stats["fixed"] / stats["total"]) * 100
            st.markdown("### Fix Progress")
            st.progress(fixed_percent / 100, f"Fixed: {fixed_percent:.1f}%")

        with col2:
            # Severity distribution
            st.markdown("### Severity Distribution")
            severity_data = {
                "Critical": stats["critical"],
                "High": stats["high"],
                "Medium": stats["medium"],
                "Low": stats["low"],
            }
            for severity, count in severity_data.items():
                percent = (count / stats["total"]) * 100
                st.progress(percent / 100, f"{severity}: {percent:.1f}%")

    st.markdown("---")

    # Error List
    st.subheader("Error List")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        severity_filter = st.selectbox(
            "Filter by Severity", ["All", "Critical", "High", "Medium", "Low"]
        )

    with col2:
        status_filter = st.selectbox(
            "Filter by Status", ["All", "Pending", "Fixing", "Fixed", "Failed"]
        )

    with col3:
        sort_by = st.selectbox("Sort by", ["Created Time", "Severity", "Status"])

    # Get tasks
    tasks = agent_status.get("tasks", [])
    error_tasks = [t for t in tasks if t.get("type") == "Fix Errors"]

    # Apply filters
    if severity_filter != "All":
        error_tasks = [
            t
            for t in error_tasks
            if t.get("error", {}).get("severity", "").lower() == severity_filter.lower()
        ]

    if status_filter != "All":
        error_tasks = [
            t
            for t in error_tasks
            if t.get("error", {}).get("status", "").lower() == status_filter.lower()
        ]

    # Sort tasks
    if sort_by == "Created Time":
        error_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    elif sort_by == "Severity":
        severity_order = {
            ErrorSeverity.CRITICAL.value: 0,
            ErrorSeverity.HIGH.value: 1,
            ErrorSeverity.MEDIUM.value: 2,
            ErrorSeverity.LOW.value: 3,
        }
        error_tasks.sort(
            key=lambda x: severity_order.get(
                x.get("error", {}).get("severity", ErrorSeverity.LOW.value), 4
            )
        )
    elif sort_by == "Status":
        status_order = {
            ErrorStatus.PENDING.value: 0,
            ErrorStatus.FIXING.value: 1,
            ErrorStatus.FAILED.value: 2,
            ErrorStatus.FIXED.value: 3,
        }
        error_tasks.sort(
            key=lambda x: status_order.get(
                x.get("error", {}).get("status", ErrorStatus.PENDING.value), 4
            )
        )

    # Display errors
    if error_tasks:
        for task in error_tasks:
            error = task.get("error", {})

            with st.expander(
                f"{error.get('message', 'Unknown error')} "
                f"({error.get('file_path', 'Unknown file')})"
            ):
                # Error details
                col1, col2, col3 = st.columns(3)

                with col1:
                    severity = error.get("severity", ErrorSeverity.HIGH.value)
                    severity_color = {
                        ErrorSeverity.CRITICAL.value: "🔴",
                        ErrorSeverity.HIGH.value: "🟡",
                        ErrorSeverity.MEDIUM.value: "🟢",
                        ErrorSeverity.LOW.value: "⚪",
                    }.get(severity, "⚪")
                    st.markdown(f"**Severity:** {severity_color} {severity}")

                    st.markdown(f"**Line:** {error.get('line_number', 'Unknown')}")

                with col2:
                    status = error.get("status", ErrorStatus.PENDING.value)
                    status_color = {
                        ErrorStatus.FIXED.value: "🟢",
                        ErrorStatus.FAILED.value: "🔴",
                        ErrorStatus.FIXING.value: "🟡",
                        ErrorStatus.PENDING.value: "⚪",
                    }.get(status, "⚪")
                    st.markdown(f"**Status:** {status_color} {status}")

                    st.markdown(
                        f"**Fix Attempts:** {error.get('fix_attempts', 0)}/"
                        f"{error.get('max_retries', 3)}"
                    )

                with col3:
                    if status == ErrorStatus.PENDING.value:
                        if st.button("Fix Now", key=f"fix_{task['id']}"):
                            # Create fix task
                            fix_task = {
                                "id": f"fix_{task['id']}",
                                "type": "Fix Error",
                                "priority": "High",
                                "error": error,
                            }
                            if assign_task(fix_task):
                                st.success("Fix task assigned")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to assign fix task")

                # Error context
                if error.get("context"):
                    st.markdown("### Context")
                    context = error["context"]

                    # Show code
                    if context.get("line_content"):
                        st.code(context["line_content"], language="python")

                    # Show scope
                    if context.get("function_name") or context.get("class_name"):
                        scope = []
                        if context.get("class_name"):
                            scope.append(f"Class: {context['class_name']}")
                        if context.get("function_name"):
                            scope.append(f"Function: {context['function_name']}")
                        st.markdown(" | ".join(scope))

                # Fix details
                if error.get("fix"):
                    st.markdown("### Fix Details")
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

                    if fix.get("verification_status"):
                        st.markdown(f"**Verification:** {fix['verification_status']}")
    else:
        st.info("No errors found matching the filters")


if __name__ == "__main__":
    main()
