"""Process management for bot subprocesses."""

import subprocess
import signal
import time
import psutil
from typing import Optional, Dict, Any, IO
from threading import Thread
import os

from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)


class ProcessManager:
    """
    Manages individual bot processes.

    Handles process lifecycle, monitoring, and resource tracking.
    """

    def __init__(self, bot_id: str, bot_name: str, bot_type: str, config: Dict[str, Any]):
        """
        Initialize process manager.

        Args:
            bot_id: Unique bot identifier
            bot_name: Bot name for logging
            bot_type: Type of bot (telegram_userbot, telegram_bot, discord_bot)
            config: Bot configuration dictionary
        """
        self.bot_id = bot_id
        self.bot_name = bot_name
        self.bot_type = bot_type
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None
        self.stdout_thread: Optional[Thread] = None
        self.stderr_thread: Optional[Thread] = None
        self.log_file: Optional[IO] = None

        # Ensure logs directory exists
        os.makedirs(settings.LOGS_DIR, exist_ok=True)
        self.log_path = os.path.join(settings.LOGS_DIR, f"{bot_id}.log")

    def start(self) -> bool:
        """
        Start the bot process.

        Returns:
            True if process started successfully, False otherwise
        """
        if self.is_running():
            logger.warning(f"Bot {self.bot_name} is already running")
            return False

        try:
            # Prepare environment variables
            env = os.environ.copy()
            env.update({
                "BOT_ID": self.bot_id,
                "BOT_TYPE": self.bot_type,
                "BOT_NAME": self.bot_name,
            })

            # Add bot-specific config to environment
            for key, value in self.config.items():
                env[key.upper()] = str(value)

            # Determine the script path based on bot type
            script_map = {
                "telegram_userbot": "telegram_userbot.py",
                "telegram_bot": "telegram_bot.py",
                "discord_bot": "discord_bot.py",
            }
            script_name = script_map.get(self.bot_type)
            if not script_name:
                logger.error(f"Unknown bot type: {self.bot_type}")
                return False

            script_path = os.path.join(settings.BOTS_DIR, "examples", script_name)

            # Open log file
            self.log_file = open(self.log_path, "a", buffering=1)

            # Start the process
            self.process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=settings.BOTS_DIR,
                text=True,
                bufsize=1
            )

            self.start_time = time.time()

            # Start output capture threads
            self.stdout_thread = Thread(
                target=self._capture_output,
                args=(self.process.stdout, "INFO"),
                daemon=True
            )
            self.stderr_thread = Thread(
                target=self._capture_output,
                args=(self.process.stderr, "ERROR"),
                daemon=True
            )
            self.stdout_thread.start()
            self.stderr_thread.start()

            logger.info(f"Started bot {self.bot_name} with PID {self.process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start bot {self.bot_name}: {e}")
            self._cleanup()
            return False

    def stop(self, force: bool = False) -> bool:
        """
        Stop the bot process.

        Args:
            force: If True, send SIGKILL instead of SIGTERM

        Returns:
            True if process stopped successfully, False otherwise
        """
        if not self.is_running():
            logger.warning(f"Bot {self.bot_name} is not running")
            return False

        try:
            if force:
                self.process.kill()
                logger.info(f"Forcefully killed bot {self.bot_name}")
            else:
                self.process.terminate()
                logger.info(f"Sent termination signal to bot {self.bot_name}")

                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=settings.BOT_SHUTDOWN_TIMEOUT)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Bot {self.bot_name} did not stop gracefully, forcing...")
                    self.process.kill()

            self._cleanup()
            return True

        except Exception as e:
            logger.error(f"Failed to stop bot {self.bot_name}: {e}")
            return False

    def restart(self) -> bool:
        """
        Restart the bot process.

        Returns:
            True if restart successful, False otherwise
        """
        logger.info(f"Restarting bot {self.bot_name}")
        self.stop()
        time.sleep(1)  # Brief pause between stop and start
        return self.start()

    def is_running(self) -> bool:
        """
        Check if process is currently running.

        Returns:
            True if process is running, False otherwise
        """
        if self.process is None:
            return False
        return self.process.poll() is None

    def get_pid(self) -> Optional[int]:
        """
        Get process ID.

        Returns:
            Process ID if running, None otherwise
        """
        if self.is_running():
            return self.process.pid
        return None

    def get_uptime(self) -> Optional[int]:
        """
        Get process uptime in seconds.

        Returns:
            Uptime in seconds if running, None otherwise
        """
        if self.is_running() and self.start_time:
            return int(time.time() - self.start_time)
        return None

    def get_resource_usage(self) -> Optional[Dict[str, float]]:
        """
        Get process resource usage (CPU, RAM).

        Returns:
            Dictionary with cpu_percent and ram_mb, or None if not running
        """
        if not self.is_running():
            return None

        try:
            process = psutil.Process(self.process.pid)
            return {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "ram_mb": process.memory_info().rss / 1024 / 1024,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def _capture_output(self, pipe: IO, level: str) -> None:
        """
        Capture output from stdout/stderr pipe.

        Args:
            pipe: Pipe to read from
            level: Log level for output
        """
        try:
            for line in iter(pipe.readline, ""):
                if line:
                    # Write to log file
                    if self.log_file and not self.log_file.closed:
                        self.log_file.write(f"[{level}] {line}")

                    # Log to console
                    if level == "ERROR":
                        logger.error(f"[{self.bot_name}] {line.strip()}")
                    else:
                        logger.info(f"[{self.bot_name}] {line.strip()}")
        except Exception as e:
            logger.error(f"Error capturing output for {self.bot_name}: {e}")
        finally:
            pipe.close()

    def _cleanup(self) -> None:
        """Clean up resources after process stops."""
        self.process = None
        self.start_time = None

        if self.log_file and not self.log_file.closed:
            self.log_file.close()
            self.log_file = None

    def __del__(self):
        """Cleanup on deletion."""
        if self.is_running():
            self.stop(force=True)
