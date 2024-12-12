import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self):
        self.setup_logging()
        self.tasks = []
        self.task_lock = asyncio.Lock()

    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_dir / "task_manager.log")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    async def create_error_fix_task(
        self, error: str, file: str, line: int, context: str
    ) -> Dict[str, Any]:
        task = {
            "type": "error_fix",
            "error": error,
            "file": file,
            "line": line,
            "context": context,
            "status": "pending",
        }
        self.tasks.append(task)
        logger.info(f"Created error fix task for {file}:{line}")
        return task

    async def create_test_execution_task(self, test_file: str) -> Dict[str, Any]:
        task = {"type": "test_execution", "test_file": test_file, "status": "pending"}
        self.tasks.append(task)
        logger.info(f"Created test execution task for {test_file}")
        return task

    async def create_linting_task(self, file: str) -> Dict[str, Any]:
        async with self.task_lock:
            # Check if there's already a pending/in-progress linting task for this file
            existing_task = next(
                (
                    task
                    for task in self.tasks
                    if task["type"] == "linting"
                    and task["file"] == file
                    and task["status"] in ["pending", "in_progress"]
                ),
                None,
            )
            if existing_task:
                return existing_task

            task = {
                "type": "linting",
                "file": file,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            self.tasks.append(task)
            logger.info(f"Created linting task for {file}")
            return task

    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        return [task for task in self.tasks if task["status"] == "pending"]

    async def update_task_status(self, task: Dict[str, Any], status: str):
        async with self.task_lock:
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            logger.info(f"Updated task status to {status} for {task['type']}")

    async def cleanup_stale_tasks(self):
        """Clean up tasks that have been in_progress for too long"""
        async with self.task_lock:
            now = datetime.now()
            for task in self.tasks:
                if task["status"] == "in_progress":
                    updated_at = datetime.fromisoformat(task["updated_at"])
                    # If task has been in progress for more than 5 minutes, mark as failed
                    if (now - updated_at).total_seconds() > 300:
                        task["status"] = "failed"
                        task["updated_at"] = now.isoformat()
                        logger.warning(f"Marked stale task as failed: {task['type']}")


task_manager = TaskManager()
