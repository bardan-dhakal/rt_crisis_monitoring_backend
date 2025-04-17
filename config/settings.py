from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
from dotenv import load_dotenv
import pathlib

# Get the root directory of the project and load .env file
ROOT_DIR = pathlib.Path(__file__).parent.parent
ENV_FILE = ROOT_DIR / '.env'
load_dotenv(dotenv_path=ENV_FILE)

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Crisis Monitoring Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True  # Set to True for debugging
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8501"]
    
    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    MONGODB_EVENTS_COLLECTION: str = "events"
    
    # Twitter API Settings
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_TOKEN_SECRET: str
    
    # News API Settings
    NEWS_API_KEY: str
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"\nError loading settings: {str(e)}")
        print(f"Looking for .env file at: {ENV_FILE}")
        print(f"File exists: {ENV_FILE.exists()}")
        raise