from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    api_title: str = "Genealogy Face Recognition Service"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://genealogy:genealogy@localhost:5432/genealogy_db"
    
    # Face Recognition
    face_recognition_enabled: bool = True
    face_recognition_model: str = "facenet"
    face_similarity_threshold: float = 0.6
    face_detection_model: str = "hog"  # hog or cnn
    
    # Storage
    upload_dir: str = "./uploads"
    faces_dir: str = "./faces"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # Backend service
    backend_service_url: str = "http://localhost:8000"
    backend_api_key: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
