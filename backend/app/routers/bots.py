"""Bot management router for CRUD and control operations."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.bot import Bot, BotStatus
from app.schemas.bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotListResponse,
    BotStatusResponse,
)
from app.schemas.log import LogListResponse, LogEntryResponse
from app.services.bot_manager import bot_manager
from app.models.log import LogEntry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/v1/bots", tags=["Bots"])


@router.get("", response_model=BotListResponse)
def list_bots(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[BotStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db)
):
    """
    List all bots with pagination and filtering.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page
        status: Optional status filter
        search: Optional name search
        db: Database session

    Returns:
        Paginated list of bots
    """
    query = db.query(Bot)

    # Apply filters
    if status:
        query = query.filter(Bot.status == status)
    if search:
        query = query.filter(Bot.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    bots = query.offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "bots": bots,
    }


@router.get("/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Get bot details by ID.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Bot details

    Raises:
        HTTPException: If bot not found
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    return bot


@router.post("", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
def create_bot(bot_data: BotCreate, db: Session = Depends(get_db)):
    """
    Create a new bot.

    Args:
        bot_data: Bot creation data
        db: Database session

    Returns:
        Created bot

    Raises:
        HTTPException: If bot name already exists
    """
    # Check if name exists
    existing_bot = db.query(Bot).filter(Bot.name == bot_data.name).first()
    if existing_bot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bot with name '{bot_data.name}' already exists"
        )

    # Create bot
    new_bot = Bot(
        name=bot_data.name,
        type=bot_data.type,
        config=bot_data.config,
        auto_restart=bot_data.auto_restart,
        status=BotStatus.STOPPED,
    )

    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)

    logger.info(f"Created new bot: {new_bot.name} (ID: {new_bot.id})")
    return new_bot


@router.put("/{bot_id}", response_model=BotResponse)
def update_bot(bot_id: str, bot_data: BotUpdate, db: Session = Depends(get_db)):
    """
    Update bot configuration.

    Args:
        bot_id: Bot ID
        bot_data: Update data
        db: Database session

    Returns:
        Updated bot

    Raises:
        HTTPException: If bot not found or running
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    # Don't allow updates while running
    if bot.status == BotStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update bot while it is running. Stop it first."
        )

    # Update fields
    if bot_data.name is not None:
        # Check name uniqueness
        existing = db.query(Bot).filter(
            Bot.name == bot_data.name,
            Bot.id != bot_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bot with name '{bot_data.name}' already exists"
            )
        bot.name = bot_data.name

    if bot_data.config is not None:
        bot.config = bot_data.config

    if bot_data.auto_restart is not None:
        bot.auto_restart = bot_data.auto_restart

    db.commit()
    db.refresh(bot)

    logger.info(f"Updated bot: {bot.name} (ID: {bot.id})")
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Delete a bot.

    Args:
        bot_id: Bot ID
        db: Database session

    Raises:
        HTTPException: If bot not found
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    # Stop bot if running
    if bot.status in [BotStatus.RUNNING, BotStatus.STARTING]:
        bot_manager.stop_bot(bot_id, db)

    # Delete from database
    db.delete(bot)
    db.commit()

    logger.info(f"Deleted bot: {bot.name} (ID: {bot.id})")
    return None


@router.post("/{bot_id}/start", response_model=BotResponse)
def start_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Start a bot process.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Updated bot with running status

    Raises:
        HTTPException: If bot not found or start fails
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    if bot.status == BotStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot is already running"
        )

    success = bot_manager.start_bot(bot_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start bot"
        )

    db.refresh(bot)
    logger.info(f"Started bot: {bot.name} (ID: {bot.id})")
    return bot


@router.post("/{bot_id}/stop", response_model=BotResponse)
def stop_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Stop a bot process.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Updated bot with stopped status

    Raises:
        HTTPException: If bot not found or stop fails
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    if bot.status == BotStatus.STOPPED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot is already stopped"
        )

    success = bot_manager.stop_bot(bot_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop bot"
        )

    db.refresh(bot)
    logger.info(f"Stopped bot: {bot.name} (ID: {bot.id})")
    return bot


@router.post("/{bot_id}/restart", response_model=BotResponse)
def restart_bot(bot_id: str, db: Session = Depends(get_db)):
    """
    Restart a bot process.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Updated bot

    Raises:
        HTTPException: If bot not found or restart fails
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    success = bot_manager.restart_bot(bot_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restart bot"
        )

    db.refresh(bot)
    logger.info(f"Restarted bot: {bot.name} (ID: {bot.id})")
    return bot


@router.get("/{bot_id}/status", response_model=BotStatusResponse)
def get_bot_status(bot_id: str, db: Session = Depends(get_db)):
    """
    Get current bot status and runtime information.

    Args:
        bot_id: Bot ID
        db: Database session

    Returns:
        Bot status information

    Raises:
        HTTPException: If bot not found
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    status_info = bot_manager.get_bot_status(bot_id)
    uptime = status_info.get("uptime") if status_info else None

    return {
        "id": bot.id,
        "name": bot.name,
        "status": bot.status,
        "process_id": bot.process_id,
        "uptime_seconds": uptime,
        "last_started_at": bot.last_started_at,
    }


@router.get("/{bot_id}/logs", response_model=LogListResponse)
def get_bot_logs(
    bot_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated bot logs from database.

    Args:
        bot_id: Bot ID
        page: Page number
        page_size: Items per page
        db: Database session

    Returns:
        Paginated log entries

    Raises:
        HTTPException: If bot not found
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )

    # Query logs
    query = db.query(LogEntry).filter(LogEntry.bot_id == bot_id).order_by(
        LogEntry.timestamp.desc()
    )

    total = query.count()
    offset = (page - 1) * page_size
    logs = query.offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "logs": logs,
    }
