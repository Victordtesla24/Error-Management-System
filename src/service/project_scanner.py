import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@asynccontextmanager
async def timeout_scanner(seconds: float):
    """Context manager for scanner timeouts"""
    try:
        yield await asyncio.wait_for(asyncio.shield(asyncio.sleep(0)), timeout=seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Scanner operation timed out after {seconds} seconds")
        raise


@dataclass
class ScanResult:
    status: str
    fixes: List[dict]


class ProjectScanner:
    async def scan_with_fixes(self, timeout: float = 30.0) -> ScanResult:
        """Scan project and generate fixes with timeout"""
        try:
            async with timeout_scanner(timeout):
                issues = await self.scan_project()
                fixes = await self.generate_fixes(issues)
                return ScanResult(status="completed", fixes=fixes)
        except asyncio.TimeoutError:
            logger.error("Project scanning timed out")
            return ScanResult(status="timeout", fixes=[])
