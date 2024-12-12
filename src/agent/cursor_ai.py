"""
Interface for communicating with Cursor AI
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class APIKeyError(Exception):
    """Raised when there are issues with the API key"""

    pass


class CursorAIInterface:
    """Interface for communicating with Cursor AI"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.retry_count = 3
        self.retry_delay = 1  # seconds
        self.timeout = 30  # seconds
        self.activities: List[Dict] = []

    def add_activity(self, activity_type: str, status: str, details: str):
        """Add a new activity to the interface's activity log"""
        activity = {
            "timestamp": time.time(),
            "type": activity_type,
            "status": status,
            "details": details,
        }
        self.activities.insert(0, activity)
        # Keep only last 100 activities
        self.activities = self.activities[:100]

    async def validate_api_key(self) -> bool:
        """Validate the API key with Cursor AI"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )

            async with self.session.get(
                f"{self.api_url}/api/validate-key", timeout=self.timeout
            ) as response:
                if response.status == 200:
                    self.add_activity(
                        "API Validation", "Success", "API key validated successfully"
                    )
                    return True
                elif response.status == 401:
                    self.add_activity("API Validation", "Error", "Invalid API key")
                    raise APIKeyError("Invalid API key")
                else:
                    self.add_activity(
                        "API Validation",
                        "Error",
                        f"API validation failed: {response.status}",
                    )
                    return False
        except Exception as e:
            self.add_activity(
                "API Validation", "Error", f"API validation error: {str(e)}"
            )
            logger.error(f"API key validation error: {e}")
            return False

    async def connect(self):
        """Establish connection with Cursor AI"""
        if self.session:
            await self.disconnect()

        try:
            # Validate API key first
            if not await self.validate_api_key():
                raise APIKeyError("Failed to validate API key")

            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            self.connected = True
            self.add_activity("Connection", "Success", "Connected to Cursor AI")
            logger.info("Connected to Cursor AI")
        except Exception as e:
            self.add_activity("Connection", "Error", f"Connection failed: {str(e)}")
            logger.error(f"Failed to connect to Cursor AI: {e}")
            raise

    async def disconnect(self):
        """Close connection with Cursor AI"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
                self.connected = False
                self.add_activity(
                    "Connection", "Success", "Disconnected from Cursor AI"
                )
                logger.info("Disconnected from Cursor AI")
            except Exception as e:
                self.add_activity("Connection", "Error", f"Disconnect error: {str(e)}")
                logger.error(f"Error disconnecting from Cursor AI: {e}")

    async def get_fix_directive(self, error: Dict) -> Optional[Dict]:
        """Get fix directive from Cursor AI for an error"""
        if not self.session or not self.connected:
            await self.connect()

        retries = 0
        while retries < self.retry_count:
            try:
                async with self.session.post(
                    f"{self.api_url}/api/cursor-ai/fix-directive",
                    json=error,
                    timeout=self.timeout,
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.add_activity(
                            "Fix Directive",
                            "Success",
                            f"Got fix directive for {error.get('file', 'unknown file')}",
                        )
                        return result
                    elif response.status == 401:
                        self.add_activity("Fix Directive", "Error", "Invalid API key")
                        raise APIKeyError("Invalid API key")
                    else:
                        self.add_activity(
                            "Fix Directive",
                            "Error",
                            f"Failed to get fix directive: {response.status}",
                        )
                        logger.error(f"Failed to get fix directive: {response.status}")

                        if response.status == 429:  # Rate limit
                            await asyncio.sleep(self.retry_delay * (retries + 1))
                            retries += 1
                            continue
                        return None

            except asyncio.TimeoutError:
                self.add_activity(
                    "Fix Directive",
                    "Error",
                    f"Timeout getting fix directive (attempt {retries + 1}/{self.retry_count})",
                )
                logger.error(
                    f"Timeout getting fix directive (attempt {retries + 1}/{self.retry_count})"
                )
                retries += 1
                if retries < self.retry_count:
                    await asyncio.sleep(self.retry_delay * retries)
                continue

            except Exception as e:
                self.add_activity(
                    "Fix Directive", "Error", f"Error getting fix directive: {str(e)}"
                )
                logger.error(f"Error getting fix directive: {e}")
                return None

        return None

    async def get_project_fixes(self, project_path: str) -> List[Dict]:
        """Get recommended fixes for an entire project"""
        if not self.session or not self.connected:
            await self.connect()

        try:
            async with self.session.post(
                f"{self.api_url}/api/cursor-ai/project-fixes",
                json={"project_path": project_path},
                timeout=self.timeout,
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.add_activity(
                        "Project Fixes",
                        "Success",
                        f"Got fixes for project {project_path}",
                    )
                    return result.get("fixes", [])
                else:
                    self.add_activity(
                        "Project Fixes",
                        "Error",
                        f"Failed to get project fixes: {response.status}",
                    )
                    logger.error(f"Failed to get project fixes: {response.status}")
                    return []
        except Exception as e:
            self.add_activity(
                "Project Fixes", "Error", f"Error getting project fixes: {str(e)}"
            )
            logger.error(f"Error getting project fixes: {e}")
            return []

    def get_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent activities"""
        return self.activities[:limit]
