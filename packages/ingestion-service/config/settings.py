from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    api_title: str = "Genealogy Ingestion Service"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # Backend service
    backend_service_url: str = "http://localhost:8000"
    backend_api_key: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # File uploads
    upload_dir: str = "./uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
