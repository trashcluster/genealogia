from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_url: str = "https://your-domain.com/telegram/webhook"
    
    # Backend service
    backend_service_url: str = "http://localhost:8000"
    backend_api_key: str = ""
    
    # Ingestion service
    ingestion_service_url: str = "http://localhost:8001"
    
    # Debug
    debug: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
