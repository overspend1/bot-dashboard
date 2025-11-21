"""Pydantic schemas for bot operations."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.bot import BotType, BotStatus


class BotCreate(BaseModel):
    """Schema for creating a new bot."""
    name: str = Field(..., min_length=1, max_length=100, description="Unique bot name")
    type: BotType = Field(..., description="Bot type (telegram_userbot, telegram_bot, discord_bot)")
    config: Dict[str, Any] = Field(..., description="Bot configuration (tokens, settings)")
    auto_restart: bool = Field(True, description="Enable automatic restart on crash")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "My Telegram Bot",
                "type": "telegram_bot",
                "config": {
                    "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                    "admin_user_ids": [12345678]
                },
                "auto_restart": True
            }
        }
    )


class BotUpdate(BaseModel):
    """Schema for updating bot configuration."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    auto_restart: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Bot Name",
                "auto_restart": False
            }
        }
    )


class BotResponse(BaseModel):
    """Schema for bot response."""
    id: str
    name: str
    type: BotType
    config: Dict[str, Any]
    status: BotStatus
    auto_restart: bool
    created_at: datetime
    updated_at: datetime
    last_started_at: Optional[datetime]
    process_id: Optional[int]
    restart_count: int
    last_crash_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class BotListResponse(BaseModel):
    """Schema for paginated bot list."""
    total: int
    page: int
    page_size: int
    bots: List[BotResponse]


class BotStatusResponse(BaseModel):
    """Schema for bot status information."""
    id: str
    name: str
    status: BotStatus
    process_id: Optional[int]
    uptime_seconds: Optional[int]
    last_started_at: Optional[datetime]
