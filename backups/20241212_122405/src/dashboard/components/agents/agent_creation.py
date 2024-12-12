"""Agent creation components."""

from typing import Any, Dict

import streamlit as st

from src.dashboard.state.agent_state import create_agent


def display_agent_creation_form() -> None:
    """Display agent creation form."""
    st.subheader("Create Agent")

    with st.form("create_agent"):
        # Agent name
        name = st.text_input("Agent Name", value="Error Management Agent")

        # Agent type
        agent_type = st.selectbox(
            "Agent Type", ["Error Detection", "Test Runner", "Code Analyzer"]
        )

        # Configuration
        st.markdown("### Agent Configuration")

        # Auto-fix settings
        auto_fix = st.checkbox("Enable Auto-Fix", value=True)
        max_retries = st.number_input(
            "Maximum Fix Retries", min_value=1, max_value=10, value=3
        )

        # Parallel processing
        parallel_fixes = st.checkbox("Enable Parallel Fixes", value=True)
        if parallel_fixes:
            max_parallel = st.number_input(
                "Maximum Parallel Fixes", min_value=1, max_value=5, value=3
            )

        # Backup settings
        backup_enabled = st.checkbox("Enable File Backups", value=True)

        # Create config
        config: Dict[str, Any] = {
            "auto_fix": auto_fix,
            "max_retries": max_retries,
            "parallel_fixes": parallel_fixes,
            "backup_enabled": backup_enabled,
        }

        if parallel_fixes:
            config["max_parallel_fixes"] = max_parallel

        # Submit button
        if st.form_submit_button("Create Agent"):
            # Create agent configuration
            agent_config = {"name": name, "type": agent_type, "config": config}

            # Create agent
            if create_agent(agent_config):
                st.success("Agent created successfully")
                st.experimental_rerun()
            else:
                st.error("Failed to create agent")
