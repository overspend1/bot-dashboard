"""Bot management service - singleton orchestrator for all bots."""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from threading import Thread, Lock
import time

from sqlalchemy.orm import Session

from app.services.process_manager import ProcessManager
from app.models.bot import Bot, BotStatus
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)


class BotManager:
    """
    Singleton manager for all bot processes.

    Handles bot lifecycle, monitoring, and crash recovery.
    """

    _instance: Optional["BotManager"] = None
    _lock: Lock = Lock()

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize bot manager."""
        if hasattr(self, "_initialized"):
            return

        self.processes: Dict[str, ProcessManager] = {}
        self.last_crash_time: Dict[str, float] = {}
        self.monitor_thread: Optional[Thread] = None
        self.running = False
        self._initialized = True
        logger.info("BotManager initialized")

    def start_monitoring(self) -> None:
        """Start background monitoring thread."""
        if self.running:
            logger.warning("Monitoring already running")
            return

        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started bot monitoring thread")

    def stop_monitoring(self) -> None:
        """Stop background monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped bot monitoring thread")

    def load_bots_from_db(self, db: Session) -> None:
        """
        Load and start bots from database that were running.

        Args:
            db: Database session
        """
        try:
            running_bots = db.query(Bot).filter(
                Bot.status.in_([BotStatus.RUNNING, BotStatus.STARTING])
            ).all()

            for bot in running_bots:
                logger.info(f"Restoring bot {bot.name} from database")
                # Reset status to stopped, then start if auto_restart is enabled
                bot.status = BotStatus.STOPPED
                db.commit()

                if bot.auto_restart:
                    self.start_bot(bot.id, db)

        except Exception as e:
            logger.error(f"Error loading bots from database: {e}")

    def start_bot(self, bot_id: str, db: Session) -> bool:
        """
        Start a bot process.

        Args:
            bot_id: Bot ID to start
            db: Database session

        Returns:
            True if started successfully, False otherwise
        """
        try:
            bot = db.query(Bot).filter(Bot.id == bot_id).first()
            if not bot:
                logger.error(f"Bot {bot_id} not found")
                return False

            if bot_id in self.processes and self.processes[bot_id].is_running():
                logger.warning(f"Bot {bot.name} is already running")
                return False

            # Update status to starting
            bot.status = BotStatus.STARTING
            db.commit()

            # Create and start process manager
            process_manager = ProcessManager(
                bot_id=bot.id,
                bot_name=bot.name,
                bot_type=bot.type.value,
                config=bot.config
            )

            if process_manager.start():
                self.processes[bot_id] = process_manager

                # Update database
                bot.status = BotStatus.RUNNING
                bot.last_started_at = datetime.utcnow()
                bot.process_id = process_manager.get_pid()
                db.commit()

                logger.info(f"Successfully started bot {bot.name}")
                return True
            else:
                bot.status = BotStatus.CRASHED
                db.commit()
                logger.error(f"Failed to start bot {bot.name}")
                return False

        except Exception as e:
            logger.error(f"Error starting bot {bot_id}: {e}")
            bot = db.query(Bot).filter(Bot.id == bot_id).first()
            if bot:
                bot.status = BotStatus.CRASHED
                db.commit()
            return False

    def stop_bot(self, bot_id: str, db: Session) -> bool:
        """
        Stop a bot process.

        Args:
            bot_id: Bot ID to stop
            db: Database session

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            bot = db.query(Bot).filter(Bot.id == bot_id).first()
            if not bot:
                logger.error(f"Bot {bot_id} not found")
                return False

            if bot_id not in self.processes:
                logger.warning(f"Bot {bot.name} process not found")
                bot.status = BotStatus.STOPPED
                bot.process_id = None
                db.commit()
                return True

            # Update status to stopping
            bot.status = BotStatus.STOPPING
            db.commit()

            # Stop the process
            process_manager = self.processes[bot_id]
            if process_manager.stop():
                del self.processes[bot_id]

                # Update database
                bot.status = BotStatus.STOPPED
                bot.process_id = None
                db.commit()

                logger.info(f"Successfully stopped bot {bot.name}")
                return True
            else:
                logger.error(f"Failed to stop bot {bot.name}")
                return False

        except Exception as e:
            logger.error(f"Error stopping bot {bot_id}: {e}")
            return False

    def restart_bot(self, bot_id: str, db: Session) -> bool:
        """
        Restart a bot process.

        Args:
            bot_id: Bot ID to restart
            db: Database session

        Returns:
            True if restarted successfully, False otherwise
        """
        logger.info(f"Restarting bot {bot_id}")
        self.stop_bot(bot_id, db)
        time.sleep(1)
        return self.start_bot(bot_id, db)

    def get_bot_status(self, bot_id: str) -> Optional[Dict]:
        """
        Get current status of a bot.

        Args:
            bot_id: Bot ID

        Returns:
            Dictionary with status information, or None if not found
        """
        if bot_id not in self.processes:
            return None

        process_manager = self.processes[bot_id]
        return {
            "is_running": process_manager.is_running(),
            "pid": process_manager.get_pid(),
            "uptime": process_manager.get_uptime(),
            "resources": process_manager.get_resource_usage(),
        }

    def get_all_bots_status(self) -> Dict[str, Dict]:
        """
        Get status of all managed bots.

        Returns:
            Dictionary mapping bot IDs to status information
        """
        return {
            bot_id: self.get_bot_status(bot_id)
            for bot_id in self.processes.keys()
        }

    def stop_all_bots(self, db: Session) -> None:
        """
        Stop all running bots gracefully.

        Args:
            db: Database session
        """
        logger.info("Stopping all bots...")
        bot_ids = list(self.processes.keys())
        for bot_id in bot_ids:
            self.stop_bot(bot_id, db)

    def _monitor_loop(self) -> None:
        """
        Background monitoring loop.

        Checks bot health and handles crash recovery.
        """
        from app.database import SessionLocal

        while self.running:
            try:
                db = SessionLocal()
                try:
                    self._check_bot_health(db)
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            time.sleep(settings.BOT_PROCESS_CHECK_INTERVAL)

    def _check_bot_health(self, db: Session) -> None:
        """
        Check health of all bots and handle crashes.

        Args:
            db: Database session
        """
        for bot_id, process_manager in list(self.processes.items()):
            try:
                bot = db.query(Bot).filter(Bot.id == bot_id).first()
                if not bot:
                    continue

                # Check if process is still running
                if not process_manager.is_running():
                    logger.warning(f"Detected crashed bot: {bot.name}")

                    # Update database
                    bot.status = BotStatus.CRASHED
                    bot.process_id = None
                    bot.last_crash_at = datetime.utcnow()
                    bot.restart_count += 1
                    db.commit()

                    # Remove from processes
                    del self.processes[bot_id]

                    # Auto-restart if enabled
                    if bot.auto_restart and settings.AUTO_RESTART_BOTS:
                        # Check backoff period
                        last_crash = self.last_crash_time.get(bot_id, 0)
                        time_since_crash = time.time() - last_crash

                        if time_since_crash > settings.BOT_RESTART_BACKOFF_SECONDS:
                            logger.info(f"Auto-restarting bot {bot.name}")
                            self.last_crash_time[bot_id] = time.time()
                            self.start_bot(bot_id, db)
                        else:
                            logger.info(
                                f"Waiting for backoff period before restarting {bot.name}"
                            )

            except Exception as e:
                logger.error(f"Error checking health of bot {bot_id}: {e}")


# Global singleton instance
bot_manager = BotManager()
