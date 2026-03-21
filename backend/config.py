from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    SECRET_KEY: str = "changeme"

    # LLM
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # Embeddings
    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    EMBED_DIMENSION: int = 384

    # User
    USER_TIMEZONE: str = "Asia/Kolkata"

    # Backup
    BACKUP_DIR: str = "./backups"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
