from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Crisis Monitoring Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8501"]  # Default Streamlit port
    
    # MongoDB Settings (loaded from environment variables)
    MONGODB_URL: str  # MongoDB Atlas connection string from .env
    MONGODB_DB_NAME: str  # Database name from .env
    MONGODB_EVENTS_COLLECTION: str = "events"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()