"""Statistics router for system and bot metrics."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bot import Bot, BotStatus
from app.schemas.stats import SystemStats, BotStats, AggregateStats
from app.services.stats_collector import StatsCollector
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])


@router.get("/system", response_model=SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """
    Get overall system statistics.

    Args:
        db: Database session

    Returns:
        System metrics including CPU, RAM, disk, network, and bot counts
    """
    # Get system metrics
    system_stats = StatsCollector.get_system_stats()

    # Get bot counts
    bots_total = db.query(Bot).count()
    bots_running = db.query(Bot).filter(Bot.status == BotStatus.RUNNING).count()
    bots_stopped = db.query(Bot).filter(Bot.status == BotStatus.STOPPED).count()
    bots_crashed = db.query(Bot).filter(Bot.status == BotStatus.CRASHED).count()

    return {
        **system_stats,
        "bots_total": bots_total,
        "bots_running": bots_running,
        "bots_stopped": bots_stopped,
        "bots_crashed": bots_crashed,
    }


@router.get("/bots/{bot_id}", response_model=BotStats)
def get_bot_stats(bot_id: str, db: Session = Depends(get_db)):
    """
    Get statistics for a specific bot.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Bot metrics including CPU, RAM, and uptime

    Raises:
        HTTPException: If bot not found or not running
    """
    # Verify bot exists
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    # Get bot stats
    stats = StatsCollector.get_bot_stats(bot_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot is not running or stats unavailable"
        )

    return {
        **stats,
        "bot_name": bot.name,
        "status": bot.status.value,
    }


@router.get("/bots", response_model=AggregateStats)
def get_all_bots_stats(db: Session = Depends(get_db)):
    """
    Get aggregate statistics for all bots.

    Args:
        db: Database session

    Returns:
        Aggregate metrics across all running bots
    """
    # Get all bot stats
    bot_stats_list = StatsCollector.get_all_bots_stats()

    # Enrich with bot names and status
    enriched_stats = []
    for bot_stat in bot_stats_list:
        bot = db.query(Bot).filter(Bot.id == bot_stat["bot_id"]).first()
        if bot:
            enriched_stats.append({
                **bot_stat,
                "bot_name": bot.name,
                "status": bot.status.value,
            })

    # Get aggregate stats
    aggregate = StatsCollector.get_aggregate_stats(enriched_stats)

    return {
        **aggregate,
        "bot_stats": enriched_stats,
    }
