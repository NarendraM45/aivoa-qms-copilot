import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL_FAST: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_REASONING: str = "llama-3.3-70b-versatile"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/pcms"
    MAX_UPLOAD_MB: int = 10
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

@lru_cache
def get_settings() -> Settings:
    return Settings()
