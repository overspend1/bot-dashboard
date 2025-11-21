"""Pydantic schemas for log entries."""

from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.log import LogLevel


class LogEntryResponse(BaseModel):
    """Schema for log entry response."""
    id: int
    bot_id: str
    timestamp: datetime
    level: LogLevel
    message: str

    model_config = ConfigDict(from_attributes=True)


class LogListResponse(BaseModel):
    """Schema for paginated log list."""
    total: int
    page: int
    page_size: int
    logs: List[LogEntryResponse]
