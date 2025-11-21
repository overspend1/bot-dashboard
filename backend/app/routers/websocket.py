"""WebSocket router for real-time log streaming."""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, Set
from datetime import datetime

from app.database import get_db
from app.models.bot import Bot
from app.services.log_collector import LogCollector
from app.services.stats_collector import StatsCollector
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)
router = APIRouter(tags=["WebSocket"])

# Active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}
stats_connections: Set[WebSocket] = set()


@router.websocket("/ws/logs/{bot_id}")
async def websocket_logs(websocket: WebSocket, bot_id: str):
    """
    WebSocket endpoint for streaming bot logs in real-time.

    Args:
        websocket: WebSocket connection
        bot_id: Bot ID to stream logs for
    """
    await websocket.accept()

    # Verify bot exists
    db: Session = next(get_db())
    try:
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            await websocket.close(code=4004, reason="Bot not found")
            return

        logger.info(f"WebSocket connection established for bot {bot.name} logs")

        # Add to active connections
        if bot_id not in active_connections:
            active_connections[bot_id] = set()
        active_connections[bot_id].add(websocket)

        # Create log collector
        log_collector = LogCollector(bot_id)

        # Send buffered logs first
        buffered_logs = log_collector.get_buffered_logs()
        for log_line in buffered_logs:
            try:
                await websocket.send_json({
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "message": log_line.strip()
                })
            except Exception as e:
                logger.error(f"Error sending buffered log: {e}")
                break

        # Stream new logs
        try:
            # Start heartbeat task
            async def heartbeat():
                while True:
                    try:
                        await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                        await websocket.send_json({"type": "ping"})
                    except Exception:
                        break

            heartbeat_task = asyncio.create_task(heartbeat())

            # Stream logs
            async for log_line in log_collector.stream_logs():
                try:
                    await websocket.send_json({
                        "timestamp": datetime.utcnow().isoformat(),
                        "level": "INFO",
                        "message": log_line.strip()
                    })
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error streaming log: {e}")
                    break

            heartbeat_task.cancel()

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for bot {bot.name}")
        except Exception as e:
            logger.error(f"WebSocket error for bot {bot.name}: {e}")
        finally:
            # Remove from active connections
            if bot_id in active_connections:
                active_connections[bot_id].discard(websocket)
                if not active_connections[bot_id]:
                    del active_connections[bot_id]

    finally:
        db.close()


@router.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """
    WebSocket endpoint for streaming system statistics in real-time.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    logger.info("WebSocket connection established for stats")

    stats_connections.add(websocket)

    try:
        # Send stats every second
        while True:
            try:
                # Get system stats
                db: Session = next(get_db())
                try:
                    from app.models.bot import BotStatus

                    system_stats = StatsCollector.get_system_stats()
                    bot_stats = StatsCollector.get_all_bots_stats()

                    # Get bot counts
                    bots_total = db.query(Bot).count()
                    bots_running = db.query(Bot).filter(Bot.status == BotStatus.RUNNING).count()
                    bots_stopped = db.query(Bot).filter(Bot.status == BotStatus.STOPPED).count()
                    bots_crashed = db.query(Bot).filter(Bot.status == BotStatus.CRASHED).count()

                    stats_data = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "system": {
                            **system_stats,
                            "bots_total": bots_total,
                            "bots_running": bots_running,
                            "bots_stopped": bots_stopped,
                            "bots_crashed": bots_crashed,
                        },
                        "bots": bot_stats,
                    }

                    await websocket.send_json(stats_data)
                finally:
                    db.close()

                await asyncio.sleep(1)

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error streaming stats: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket error for stats: {e}")
    finally:
        stats_connections.discard(websocket)
        logger.info("WebSocket disconnected for stats")


async def broadcast_log(bot_id: str, log_data: dict):
    """
    Broadcast a log message to all connected clients for a bot.

    Args:
        bot_id: Bot ID
        log_data: Log data to broadcast
    """
    if bot_id in active_connections:
        disconnected = set()
        for websocket in active_connections[bot_id]:
            try:
                await websocket.send_json(log_data)
            except Exception:
                disconnected.add(websocket)

        # Clean up disconnected clients
        active_connections[bot_id] -= disconnected
        if not active_connections[bot_id]:
            del active_connections[bot_id]
