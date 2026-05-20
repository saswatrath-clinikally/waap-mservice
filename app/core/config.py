from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "Wapp Middleware"
    API_V1_STR: str = "/api/v1"
    
    # CORS setup
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # External Backend config
    OTHER_BACKEND_URL: str = "http://localhost:8080"
    OTHER_BACKEND_API_KEY: str = "dermagptsecretkey123#"

    # Optional Database config
    # DATABASE_URI: str = "postgresql+asyncpg://user:password@localhost/dbname"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
