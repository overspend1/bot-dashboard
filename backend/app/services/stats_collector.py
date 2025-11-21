"""Statistics collection service for system and bot metrics."""

import psutil
from typing import Dict, Any, List, Optional

from app.services.bot_manager import bot_manager
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class StatsCollector:
    """
    Collects system and bot statistics.

    Provides metrics like CPU, RAM, disk, network usage.
    """

    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """
        Get overall system statistics.

        Returns:
            Dictionary with system metrics
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory
            memory = psutil.virtual_memory()
            ram_used_mb = memory.used / 1024 / 1024
            ram_total_mb = memory.total / 1024 / 1024
            ram_percent = memory.percent

            # Disk
            disk = psutil.disk_usage("/")
            disk_used_gb = disk.used / 1024 / 1024 / 1024
            disk_total_gb = disk.total / 1024 / 1024 / 1024
            disk_percent = disk.percent

            # Network
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / 1024 / 1024
            network_recv_mb = network.bytes_recv / 1024 / 1024

            return {
                "cpu_percent": round(cpu_percent, 2),
                "ram_used_mb": round(ram_used_mb, 2),
                "ram_total_mb": round(ram_total_mb, 2),
                "ram_percent": round(ram_percent, 2),
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_total_gb": round(disk_total_gb, 2),
                "disk_percent": round(disk_percent, 2),
                "network_sent_mb": round(network_sent_mb, 2),
                "network_recv_mb": round(network_recv_mb, 2),
            }

        except Exception as e:
            logger.error(f"Error collecting system stats: {e}")
            return {}

    @staticmethod
    def get_bot_stats(bot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific bot.

        Args:
            bot_id: Bot ID

        Returns:
            Dictionary with bot metrics, or None if bot not found
        """
        try:
            status = bot_manager.get_bot_status(bot_id)
            if not status or not status["is_running"]:
                return None

            resources = status.get("resources", {})
            return {
                "bot_id": bot_id,
                "cpu_percent": round(resources.get("cpu_percent", 0), 2),
                "ram_mb": round(resources.get("ram_mb", 0), 2),
                "uptime_seconds": status.get("uptime"),
            }

        except Exception as e:
            logger.error(f"Error collecting stats for bot {bot_id}: {e}")
            return None

    @staticmethod
    def get_all_bots_stats() -> List[Dict[str, Any]]:
        """
        Get statistics for all bots.

        Returns:
            List of bot statistics dictionaries
        """
        all_status = bot_manager.get_all_bots_status()
        stats = []

        for bot_id, status in all_status.items():
            if status and status["is_running"]:
                bot_stat = StatsCollector.get_bot_stats(bot_id)
                if bot_stat:
                    stats.append(bot_stat)

        return stats

    @staticmethod
    def get_aggregate_stats(bot_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get aggregate statistics across all bots.

        Args:
            bot_stats: List of individual bot statistics

        Returns:
            Dictionary with aggregate metrics
        """
        if not bot_stats:
            return {
                "total_bots": 0,
                "total_cpu_percent": 0,
                "total_ram_mb": 0,
                "average_uptime_seconds": None,
            }

        total_cpu = sum(stat.get("cpu_percent", 0) for stat in bot_stats)
        total_ram = sum(stat.get("ram_mb", 0) for stat in bot_stats)

        uptimes = [stat.get("uptime_seconds") for stat in bot_stats if stat.get("uptime_seconds")]
        avg_uptime = sum(uptimes) / len(uptimes) if uptimes else None

        return {
            "total_bots": len(bot_stats),
            "total_cpu_percent": round(total_cpu, 2),
            "total_ram_mb": round(total_ram, 2),
            "average_uptime_seconds": round(avg_uptime, 2) if avg_uptime else None,
        }
