from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/genealogy"
    
    # API
    api_title: str = "Genealogy API"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Services
    ingestion_service_url: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
