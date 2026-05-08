"""Configuration management module."""
import os
from dataclasses import dataclass
from typing import Optional
from functools import lru_cache


@dataclass
class Config:
    """Application configuration."""

    # Google Services
    GEMINI_API_KEY: str
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None

    # Firestore
    FIRESTORE_DATABASE: str = "(default)"
    USE_FIRESTORE: bool = False

    # Application
    APP_NAME: str = "AI Travel Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4

    # API
    API_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT: int = 100

    # Features
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600
    ENABLE_WEATHER: bool = True
    ENABLE_TRAFFIC: bool = False
    ENABLE_EVENTS: bool = True

    # Security
    ALLOWED_ORIGINS: list = None
    API_KEY_HEADER: str = "X-API-Key"
    MAX_REQUEST_SIZE: int = 1048576  # 1MB

    def __post_init__(self):
        """Validate and setup configuration."""
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        if self.ALLOWED_ORIGINS is None:
            self.ALLOWED_ORIGINS = ["*"]

    @staticmethod
    @lru_cache(maxsize=1)
    def from_env() -> "Config":
        """Load configuration from environment variables."""
        return Config(
            GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
            GOOGLE_MAPS_API_KEY=os.getenv("GOOGLE_MAPS_API_KEY"),
            GOOGLE_CLOUD_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT"),
            FIRESTORE_DATABASE=os.getenv("FIRESTORE_DATABASE", "(default)"),
            USE_FIRESTORE=os.getenv("USE_FIRESTORE", "false").lower() == "true",
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8080")),
            ENABLE_CACHING=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            CACHE_TTL=int(os.getenv("CACHE_TTL", "3600")),
            ENABLE_WEATHER=os.getenv("ENABLE_WEATHER", "true").lower() == "true",
            ENABLE_TRAFFIC=os.getenv("ENABLE_TRAFFIC", "false").lower() == "true",
            ENABLE_EVENTS=os.getenv("ENABLE_EVENTS", "true").lower() == "true",
        )
