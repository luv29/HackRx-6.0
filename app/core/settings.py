import os
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    """Application settings.
    
    Attributes:
        app_name: Name of the application
        gemini_api_key: Gemini API key
        supabase_url: URL of supabase
        supabase_service_key: The secret token of supabase
        debug: Debug mode flag
    """
    app_name: str = "HackRx 6.0"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    debug: bool = bool(os.getenv("DEBUG", False))
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()

logging.basicConfig(
    level=logging.INFO if not get_settings().debug else logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
) 