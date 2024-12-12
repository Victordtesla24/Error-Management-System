import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class MonitoringResult:
    status: str
    agents: List[Dict[str, Any]]


@asynccontextmanager
async def get_dashboard_service():
    """Context manager for dashboard service"""
    from src.dashboard.service import DashboardService

    service = await DashboardService.create()
    try:
        yield service
    finally:
        await service.stop()


async def get_active_agents() -> List[Dict[str, Any]]:
    """Get list of currently active agents"""
    async with get_dashboard_service() as service:
        agents = []
        for agent_id, agent in service.agents.items():
            try:
                last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
                if datetime.now() - last_heartbeat < timedelta(seconds=30):
                    agents.append({"id": agent_id, "status": "active", **agent})
                else:
                    # Add inactive agents too, but mark them as inactive
                    agents.append({"id": agent_id, "status": "inactive", **agent})
            except (ValueError, KeyError) as e:
                logger.error(f"Error processing agent {agent_id}: {e}")
                # Include agent with error status
                agents.append({"id": agent_id, "status": "error", **agent})
        return agents


async def check_agents_status(agents: List[Dict[str, Any]]) -> bool:
    """Check status of all agents"""
    try:
        if not agents:
            return False
        return any(agent["status"] == "active" for agent in agents)
    except Exception as e:
        logger.error(f"Error checking agent status: {e}")
        return False


async def monitor_agents():
    """Monitor agents and return their status"""
    MAX_WAIT = 25  # Maximum wait time in seconds

    start_time = time.time()
    while time.time() - start_time < MAX_WAIT:
        try:
            agents = await get_active_agents()
            status = await check_agents_status(agents)

            # Always return a result, but with appropriate status
            return MonitoringResult(
                status="completed" if status else "warning", agents=agents
            )

        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(0.1)  # Add small delay on error

    return MonitoringResult(status="timeout", agents=[])
