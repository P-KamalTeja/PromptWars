"""Configuration management module."""
import os
from dataclasses import dataclass
from typing import Optional
from functools import lru_cache

try:
    from google.cloud import secretmanager
    HAS_SECRET_MANAGER = True
except ImportError:
    HAS_SECRET_MANAGER = False


@dataclass
class Config:
    """Application configuration."""

    # Google Services
    GEMINI_API_KEY: str
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GCS_BUCKET_NAME: Optional[str] = None
    USE_VERTEX_AI: bool = False

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
            raise ValueError("GEMINI_API_KEY environment variable or secret is required")

        if self.ALLOWED_ORIGINS is None:
            self.ALLOWED_ORIGINS = ["*"]

    @staticmethod
    @lru_cache(maxsize=1)
    def from_env() -> "Config":
        """Load configuration from environment variables or Secret Manager."""
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        def get_val(key: str, default: Optional[str] = None) -> Optional[str]:
            val = os.getenv(key)
            if val:
                return val
            
            # Try Secret Manager if on GCP
            if HAS_SECRET_MANAGER and project_id:
                try:
                    client = secretmanager.SecretManagerServiceClient()
                    name = f"projects/{project_id}/secrets/{key}/versions/latest"
                    response = client.access_secret_version(request={"name": name})
                    return response.payload.data.decode("UTF-8")
                except Exception:
                    pass
            return default

        return Config(
            GEMINI_API_KEY=get_val("GEMINI_API_KEY", ""),
            GOOGLE_MAPS_API_KEY=get_val("GOOGLE_MAPS_API_KEY"),
            GOOGLE_CLOUD_PROJECT=project_id,
            GCS_BUCKET_NAME=get_val("GCS_BUCKET_NAME"),
            USE_VERTEX_AI=get_val("USE_VERTEX_AI", "false").lower() == "true",
            FIRESTORE_DATABASE=get_val("FIRESTORE_DATABASE", "(default)"),
            USE_FIRESTORE=get_val("USE_FIRESTORE", "false").lower() == "true",
            DEBUG=get_val("DEBUG", "false").lower() == "true",
            LOG_LEVEL=get_val("LOG_LEVEL", "INFO"),
            HOST=get_val("HOST", "0.0.0.0"),
            PORT=int(get_val("PORT", "8080")),
            ENABLE_CACHING=get_val("ENABLE_CACHING", "true").lower() == "true",
            CACHE_TTL=int(get_val("CACHE_TTL", "3600")),
            ENABLE_WEATHER=get_val("ENABLE_WEATHER", "true").lower() == "true",
            ENABLE_TRAFFIC=get_val("ENABLE_TRAFFIC", "false").lower() == "true",
            ENABLE_EVENTS=get_val("ENABLE_EVENTS", "true").lower() == "true",
        )
