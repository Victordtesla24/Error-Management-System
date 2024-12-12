"""Main agent module."""

import asyncio
import logging
import sys
from pathlib import Path

from src.error_management.agent_manager import agent_manager
from src.error_management.error_detector import ErrorDetector
from src.error_management.error_fixer import ErrorFixer


async def main():
    """Run the agent."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/agent.log"),
        ],
    )
    logger = logging.getLogger(__name__)

    try:
        # Initialize components
        project_path = Path.cwd()
        error_detector = ErrorDetector(project_path)
        ErrorFixer()

        # Add monitored paths
        error_detector.add_monitored_path(project_path / "src")
        error_detector.add_monitored_path(project_path / "tests")

        # Create agent
        agent_config = {
            "name": "Error Management Agent",
            "type": "Error Management",
            "config": {
                "auto_fix": True,
                "monitoring": {"enabled": True, "interval": 5},
            },
        }
        agent_id = agent_manager.create_agent(agent_config)
        if not agent_id:
            raise Exception("Failed to create agent")

        logger.info("Agent started successfully")

        # Main loop
        while True:
            # Detect errors
            errors = error_detector.scan_for_errors()
            if errors:
                logger.info(f"Found {len(errors)} errors")
                for error in errors:
                    # Create fix task
                    task = {
                        "id": f"fix_{error.id}",
                        "type": "Fix Error",
                        "priority": "High",
                        "error": error.to_dict(),
                        "config": {"auto_fix": True, "backup": True},
                    }
                    # Assign task to agent
                    agent_manager.assign_task(agent_id, task)
                    logger.info(f"Created fix task for error: {error.message}")

            # Sleep before next scan
            await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
