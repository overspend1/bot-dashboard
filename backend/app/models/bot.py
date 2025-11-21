"""Bot model for database."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class BotType(str, enum.Enum):
    """Supported bot types."""
    TELEGRAM_USERBOT = "telegram_userbot"
    TELEGRAM_BOT = "telegram_bot"
    DISCORD_BOT = "discord_bot"


class BotStatus(str, enum.Enum):
    """Bot operational status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CRASHED = "crashed"


class Bot(Base):
    """Bot model representing a managed bot instance."""

    __tablename__ = "bots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(BotType), nullable=False)
    config = Column(JSON, nullable=False)
    status = Column(SQLEnum(BotStatus), default=BotStatus.STOPPED, nullable=False)
    auto_restart = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_started_at = Column(DateTime, nullable=True)
    process_id = Column(Integer, nullable=True)
    restart_count = Column(Integer, default=0, nullable=False)
    last_crash_at = Column(DateTime, nullable=True)

    # Relationships
    logs = relationship("LogEntry", back_populates="bot", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Bot(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"
