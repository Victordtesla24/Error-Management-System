"""Agent state management."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

from src.error_management.agent_manager import agent_manager
from src.error_management.models import AgentMetrics, ErrorSeverity, ErrorStatus


def initialize_session_state():
    """Initialize session state."""
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
        st.session_state.agent_id = None
        st.session_state.last_update = None
        st.session_state.error_count = 0
        st.session_state.success_count = 0
        st.session_state.metrics_history = []


def get_agent_status() -> Optional[Dict[str, Any]]:
    """Get current agent status."""
    try:
        if not st.session_state.agent_id:
            return None

        return agent_manager.get_agent_status(st.session_state.agent_id)
    except Exception as e:
        logging.error(f"Failed to get agent status: {str(e)}")
        return None


def get_agent_metrics() -> Optional[AgentMetrics]:
    """Get current agent metrics."""
    try:
        if not st.session_state.agent_id:
            return None

        metrics = agent_manager.get_agent_metrics(st.session_state.agent_id)

        # Update metrics history
        if metrics:
            st.session_state.metrics_history.append(
                {"timestamp": datetime.now(), "metrics": metrics}
            )

            # Keep last 100 metrics
            if len(st.session_state.metrics_history) > 100:
                st.session_state.metrics_history.pop(0)

        return metrics
    except Exception as e:
        logging.error(f"Failed to get agent metrics: {str(e)}")
        return None


def get_agent_tasks() -> List[Dict[str, Any]]:
    """Get current agent tasks."""
    try:
        if not st.session_state.agent_id:
            return []

        return agent_manager.get_agent_tasks(st.session_state.agent_id)
    except Exception as e:
        logging.error(f"Failed to get agent tasks: {str(e)}")
        return []


def get_agent_logs() -> List[Dict[str, Any]]:
    """Get agent logs."""
    try:
        if not st.session_state.agent_id:
            return []

        return agent_manager.get_agent_logs(st.session_state.agent_id)
    except Exception as e:
        logging.error(f"Failed to get agent logs: {str(e)}")
        return []


def create_agent(config: Dict[str, Any]) -> bool:
    """Create new agent."""
    try:
        agent_id = agent_manager.create_agent(config)
        if agent_id:
            st.session_state.agent_id = agent_id
            st.session_state.agent_initialized = True
            st.session_state.last_update = datetime.now()
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to create agent: {str(e)}")
        return False


def start_agent() -> bool:
    """Start agent."""
    try:
        if not st.session_state.agent_id:
            return False

        return agent_manager.start_agent(st.session_state.agent_id)
    except Exception as e:
        logging.error(f"Failed to start agent: {str(e)}")
        return False


def stop_agent() -> bool:
    """Stop agent."""
    try:
        if not st.session_state.agent_id:
            return False

        return agent_manager.stop_agent(st.session_state.agent_id)
    except Exception as e:
        logging.error(f"Failed to stop agent: {str(e)}")
        return False


def assign_task(task: Dict[str, Any]) -> bool:
    """Assign task to agent."""
    try:
        if not st.session_state.agent_id:
            return False

        return agent_manager.assign_task(st.session_state.agent_id, task)
    except Exception as e:
        logging.error(f"Failed to assign task: {str(e)}")
        return False


def get_error_stats() -> Dict[str, int]:
    """Get error statistics."""
    try:
        tasks = get_agent_tasks()
        error_tasks = [t for t in tasks if t.get("type") == "Fix Errors"]

        stats = {
            "total": len(error_tasks),
            "pending": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("status") == ErrorStatus.PENDING.value
                ]
            ),
            "fixing": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("status") == ErrorStatus.FIXING.value
                ]
            ),
            "fixed": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("status") == ErrorStatus.FIXED.value
                ]
            ),
            "failed": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("status") == ErrorStatus.FAILED.value
                ]
            ),
            "critical": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("severity")
                    == ErrorSeverity.CRITICAL.value
                ]
            ),
            "high": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("severity") == ErrorSeverity.HIGH.value
                ]
            ),
            "medium": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("severity") == ErrorSeverity.MEDIUM.value
                ]
            ),
            "low": len(
                [
                    t
                    for t in error_tasks
                    if t.get("error", {}).get("severity") == ErrorSeverity.LOW.value
                ]
            ),
        }

        return stats
    except Exception as e:
        logging.error(f"Failed to get error stats: {str(e)}")
        return {
            "total": 0,
            "pending": 0,
            "fixing": 0,
            "fixed": 0,
            "failed": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }


def get_performance_stats() -> Dict[str, float]:
    """Get performance statistics."""
    try:
        metrics = get_agent_metrics()
        if not metrics:
            return {}

        return {
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "response_time": metrics.response_time,
            "success_rate": metrics.success_rate,
        }
    except Exception as e:
        logging.error(f"Failed to get performance stats: {str(e)}")
        return {}
