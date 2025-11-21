"""Application configuration using pydantic-settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./data/bot_dashboard.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    LOG_LEVEL: str = "INFO"
    MAX_LOG_SIZE_MB: int = 10

    # Bot Management
    AUTO_RESTART_BOTS: bool = True
    STATS_COLLECTION_INTERVAL: int = 5
    BOT_PROCESS_CHECK_INTERVAL: int = 5
    BOT_RESTART_BACKOFF_SECONDS: int = 10
    BOT_SHUTDOWN_TIMEOUT: int = 10

    # Paths
    BOTS_DIR: str = "./bots"
    LOGS_DIR: str = "./bots/logs"
    CONFIGS_DIR: str = "./bots/configs"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_LOG_BUFFER_SIZE: int = 100

    # Rate Limiting
    RATE_LIMIT_PER_SECOND: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
