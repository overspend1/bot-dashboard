"""Log entry model for database."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class LogLevel(str, enum.Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(Base):
    """Log entry model for bot logs."""

    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(String(36), ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)

    # Relationships
    bot = relationship("Bot", back_populates="logs")

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, bot_id={self.bot_id}, level={self.level})>"
