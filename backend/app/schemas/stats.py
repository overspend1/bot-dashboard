"""Pydantic schemas for statistics."""

from typing import Optional, List
from pydantic import BaseModel, Field


class SystemStats(BaseModel):
    """Schema for system-wide statistics."""
    cpu_percent: float = Field(..., description="Overall CPU usage percentage")
    ram_used_mb: float = Field(..., description="RAM used in megabytes")
    ram_total_mb: float = Field(..., description="Total RAM in megabytes")
    ram_percent: float = Field(..., description="RAM usage percentage")
    disk_used_gb: float = Field(..., description="Disk used in gigabytes")
    disk_total_gb: float = Field(..., description="Total disk in gigabytes")
    disk_percent: float = Field(..., description="Disk usage percentage")
    network_sent_mb: float = Field(..., description="Network data sent in MB")
    network_recv_mb: float = Field(..., description="Network data received in MB")
    bots_total: int = Field(..., description="Total number of bots")
    bots_running: int = Field(..., description="Number of running bots")
    bots_stopped: int = Field(..., description="Number of stopped bots")
    bots_crashed: int = Field(..., description="Number of crashed bots")


class BotStats(BaseModel):
    """Schema for individual bot statistics."""
    bot_id: str
    bot_name: str
    cpu_percent: Optional[float] = Field(None, description="Bot CPU usage percentage")
    ram_mb: Optional[float] = Field(None, description="Bot RAM usage in MB")
    uptime_seconds: Optional[int] = Field(None, description="Bot uptime in seconds")
    status: str


class AggregateStats(BaseModel):
    """Schema for aggregate bot statistics."""
    total_bots: int
    total_cpu_percent: float
    total_ram_mb: float
    average_uptime_seconds: Optional[float]
    bot_stats: List[BotStats]
