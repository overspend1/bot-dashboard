"""Log collection service for bot logs."""

import os
from typing import List, Optional, AsyncIterator
from collections import deque
import asyncio
import aiofiles

from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LogCollector:
    """
    Collects and streams bot logs.

    Maintains a buffer of recent logs and can stream new logs in real-time.
    """

    def __init__(self, bot_id: str, buffer_size: int = 100):
        """
        Initialize log collector.

        Args:
            bot_id: Bot ID to collect logs for
            buffer_size: Number of recent log lines to buffer
        """
        self.bot_id = bot_id
        self.buffer_size = buffer_size
        self.log_buffer: deque = deque(maxlen=buffer_size)
        self.log_path = os.path.join(settings.LOGS_DIR, f"{bot_id}.log")
        self.subscribers: List[asyncio.Queue] = []
        self._load_recent_logs()

    def _load_recent_logs(self) -> None:
        """Load recent logs from file into buffer."""
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, "r") as f:
                    # Read last N lines
                    lines = deque(f, maxlen=self.buffer_size)
                    self.log_buffer.extend(lines)
                logger.info(f"Loaded {len(self.log_buffer)} recent log lines for bot {self.bot_id}")
        except Exception as e:
            logger.error(f"Error loading recent logs for bot {self.bot_id}: {e}")

    def get_buffered_logs(self) -> List[str]:
        """
        Get buffered log lines.

        Returns:
            List of recent log lines
        """
        return list(self.log_buffer)

    async def read_logs(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[str]:
        """
        Read logs from file with pagination.

        Args:
            offset: Number of lines to skip from start
            limit: Maximum number of lines to return

        Returns:
            List of log lines
        """
        try:
            if not os.path.exists(self.log_path):
                return []

            async with aiofiles.open(self.log_path, "r") as f:
                lines = await f.readlines()
                return lines[offset:offset + limit]

        except Exception as e:
            logger.error(f"Error reading logs for bot {self.bot_id}: {e}")
            return []

    async def stream_logs(self) -> AsyncIterator[str]:
        """
        Stream new log lines as they arrive.

        Yields:
            New log lines
        """
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers.append(queue)

        try:
            while True:
                line = await queue.get()
                yield line
        finally:
            self.subscribers.remove(queue)

    async def publish_log(self, line: str) -> None:
        """
        Publish a new log line to all subscribers.

        Args:
            line: Log line to publish
        """
        # Add to buffer
        self.log_buffer.append(line)

        # Notify all subscribers
        for queue in self.subscribers:
            try:
                await queue.put(line)
            except Exception as e:
                logger.error(f"Error publishing log to subscriber: {e}")

    async def tail_logs(self, lines: int = 50) -> List[str]:
        """
        Get the last N lines from log file.

        Args:
            lines: Number of lines to retrieve

        Returns:
            List of last N log lines
        """
        try:
            if not os.path.exists(self.log_path):
                return []

            async with aiofiles.open(self.log_path, "r") as f:
                content = await f.read()
                all_lines = content.splitlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines

        except Exception as e:
            logger.error(f"Error tailing logs for bot {self.bot_id}: {e}")
            return []

    def clear_logs(self) -> bool:
        """
        Clear log file for this bot.

        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.log_path):
                open(self.log_path, "w").close()
                self.log_buffer.clear()
                logger.info(f"Cleared logs for bot {self.bot_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing logs for bot {self.bot_id}: {e}")
            return False
