from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NL-SQL Analyst"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4173",
    ]

    # Database
    DB_PATH: str = str(BASE_DIR / "data" / "analyst.db")

    # Claude
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-opus-4-5"
    MAX_TOKENS: int = 1024

    # Query safety
    MAX_ROWS_RETURNED: int = 500
    QUERY_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
