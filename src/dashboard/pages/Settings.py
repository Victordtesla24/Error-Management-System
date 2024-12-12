"""System settings and configuration page."""

import streamlit as st
import yaml

from src.dashboard.state.agent_state import get_agent_status, initialize_session_state
from src.error_management.models import ErrorSeverity


def load_config():
    """Load current configuration."""
    try:
        with open("error_management_config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


def save_config(config):
    """Save configuration."""
    try:
        with open("error_management_config.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception:
        return False


def main():
    """Main settings page."""
    st.title("System Settings")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Get agent status
    agent_status = get_agent_status()
    if not agent_status:
        st.warning("No agent is currently running")
        st.markdown("Create an agent from the home page to get started.")
        return

    # Load current configuration
    config = load_config()

    # Create settings sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Agent Settings", "Error Management", "Performance", "System"]
    )

    # Agent Settings
    with tab1:
        st.subheader("Agent Configuration")

        # Auto-fix settings
        auto_fix = st.toggle(
            "Enable Auto-Fix", value=config.get("agent", {}).get("auto_fix", True)
        )

        max_retries = st.number_input(
            "Maximum Fix Retries",
            min_value=1,
            max_value=10,
            value=config.get("agent", {}).get("max_retries", 3),
        )

        parallel_fixes = st.toggle(
            "Enable Parallel Fixes",
            value=config.get("agent", {}).get("parallel_fixes", True),
        )

        if parallel_fixes:
            max_parallel = st.number_input(
                "Maximum Parallel Fixes",
                min_value=1,
                max_value=5,
                value=config.get("agent", {}).get("max_parallel_fixes", 3),
            )

        backup_enabled = st.toggle(
            "Enable File Backups",
            value=config.get("agent", {}).get("backup_enabled", True),
        )

        # Update agent config
        config["agent"] = {
            "auto_fix": auto_fix,
            "max_retries": max_retries,
            "parallel_fixes": parallel_fixes,
            "max_parallel_fixes": max_parallel if parallel_fixes else 1,
            "backup_enabled": backup_enabled,
        }

    # Error Management
    with tab2:
        st.subheader("Error Management Settings")

        # Scan settings
        st.markdown("### Error Detection")
        scan_interval = st.number_input(
            "Scan Interval (seconds)",
            min_value=10,
            max_value=300,
            value=config.get("error_detection", {}).get("scan_interval", 30),
        )

        file_patterns = st.text_area(
            "File Patterns to Monitor",
            value="\n".join(
                config.get("error_detection", {}).get(
                    "file_patterns", ["*.py", "*.yaml", "*.json"]
                )
            ),
        )

        ignore_patterns = st.text_area(
            "Patterns to Ignore",
            value="\n".join(
                config.get("error_detection", {}).get(
                    "ignore_patterns", ["__pycache__", "*.pyc", "venv", ".git"]
                )
            ),
        )

        # Severity settings
        st.markdown("### Error Severity Settings")
        severity_settings = {}

        for severity in ErrorSeverity:
            st.markdown(f"#### {severity.value.title()}")
            col1, col2, col3 = st.columns(3)

            with col1:
                auto_fix = st.toggle(
                    f"Auto-fix {severity.value}",
                    value=config.get("error_detection", {})
                    .get("severity_levels", {})
                    .get(severity.value, {})
                    .get("auto_fix", True),
                )

            with col2:
                notify = st.toggle(
                    f"Notify on {severity.value}",
                    value=config.get("error_detection", {})
                    .get("severity_levels", {})
                    .get(severity.value, {})
                    .get("notify", True),
                )

            with col3:
                retry_count = st.number_input(
                    f"Retry count for {severity.value}",
                    min_value=1,
                    max_value=5,
                    value=config.get("error_detection", {})
                    .get("severity_levels", {})
                    .get(severity.value, {})
                    .get("retry_count", 3),
                )

            severity_settings[severity.value] = {
                "auto_fix": auto_fix,
                "notify": notify,
                "retry_count": retry_count,
            }

        # Update error detection config
        config["error_detection"] = {
            "scan_interval": scan_interval,
            "file_patterns": file_patterns.split("\n"),
            "ignore_patterns": ignore_patterns.split("\n"),
            "severity_levels": severity_settings,
        }

    # Performance Settings
    with tab3:
        st.subheader("Performance Settings")

        # Memory settings
        st.markdown("### Memory Management")
        max_memory = st.number_input(
            "Maximum Memory Usage (%)",
            min_value=50,
            max_value=95,
            value=config.get("memory", {}).get("max_usage", 80),
        )

        gc_threshold = st.number_input(
            "Garbage Collection Threshold (%)",
            min_value=50,
            max_value=90,
            value=config.get("memory", {}).get("gc_threshold", 70),
        )

        # Performance thresholds
        st.markdown("### Performance Thresholds")
        cpu_threshold = st.number_input(
            "CPU Usage Threshold (%)",
            min_value=50,
            max_value=95,
            value=config.get("performance", {}).get("cpu_threshold", 80),
        )

        response_time = st.number_input(
            "Maximum Response Time (seconds)",
            min_value=0.1,
            max_value=5.0,
            value=config.get("performance", {}).get("response_time", 1.0),
        )

        # Update performance config
        config["memory"] = {
            "max_usage": max_memory,
            "gc_threshold": gc_threshold,
            "monitoring_interval": 60,
        }

        config["performance"] = {
            "cpu_threshold": cpu_threshold,
            "response_time": response_time,
            "batch_size": 100,
            "queue_size": 1000,
            "timeout": 30,
        }

    # System Settings
    with tab4:
        st.subheader("System Settings")

        # Logging settings
        st.markdown("### Logging")
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(
                config.get("logging", {}).get("level", "INFO")
            ),
        )

        backup_count = st.number_input(
            "Log Backup Count",
            min_value=1,
            max_value=10,
            value=config.get("logging", {}).get("backup_count", 5),
        )

        # Documentation settings
        st.markdown("### Documentation")
        auto_docs = st.toggle(
            "Auto-generate Documentation",
            value=config.get("documentation", {}).get("auto_generate", True),
        )

        doc_formats = st.multiselect(
            "Documentation Formats",
            ["markdown", "html"],
            default=config.get("documentation", {}).get(
                "formats", ["markdown", "html"]
            ),
        )

        # Update system config
        config["logging"] = {
            "level": log_level,
            "file": "logs/error_management.log",
            "max_size": "10MB",
            "backup_count": backup_count,
            "format": "%(asctime)s [%(levelname)s] %(message)s",
        }

        config["documentation"] = {
            "auto_generate": auto_docs,
            "formats": doc_formats,
            "include_metrics": True,
            "include_fixes": True,
            "output_dir": "docs/",
        }

    # Save button
    st.markdown("---")
    if st.button("Save Settings"):
        if save_config(config):
            st.success("Settings saved successfully")
            st.info("Restart the agent for changes to take effect")
        else:
            st.error("Failed to save settings")
