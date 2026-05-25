from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Wapp Middleware"
    API_V1_STR: str = "/api/v1"

    # CORS setup
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # External Backend config
    CLINTEL_BACKEND_URL: str = "http://localhost:8080"
    CLINTEL_BACKEND_API_KEY: str

    # Anthropic transform config
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 512

    # Optional Database config
    # DATABASE_URI: str = "postgresql+asyncpg://user:password@localhost/dbname"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Instantiate settings but tell mypy to ignore instantiation checks 
# because Pydantic populates these fields from the environment
settings = Settings()  # type: ignore
