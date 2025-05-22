from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Theme Identifier"
    
    # File Storage
    UPLOAD_DIR: str = "files"
    VECTOR_STORE_DIR: str = "data/vectorstore"
    
    # Model Settings
    OPENAI_API_KEY: str = "ENTER_YOUR_OPENAI_API_KEY"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

# Create necessary directories
Path(Settings().UPLOAD_DIR).mkdir(exist_ok=True)
Path(Settings().VECTOR_STORE_DIR).mkdir(parents=True, exist_ok=True)