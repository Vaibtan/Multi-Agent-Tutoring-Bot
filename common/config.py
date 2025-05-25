import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    HOST: str = "0.0.0.0"
    TUTOR_PORT: int = 8000
    A2A_BASE_URL: str = "http://localhost"
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding = "utf-8", \
        extra = "ignore", case_sensitive = False)
settings = Settings()
