from pydantic import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    HOST: str = "0.0.0.0"
    TUTOR_PORT: int = 8000
    MATH_PORT: int = 8001
    PHYSICS_PORT: int = 8002
    A2A_BASE_URL: str = "http://localhost"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    API_KEY_HEADER: str = "X-API-Key"

    class Config:
        env_file = ".env"

settings = Settings()
