"""Application configuration settings."""
import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sitesage")
    )

    # Groq AI
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY", ""))
    groq_model: str = "llama-3.3-70b-versatile"

    # Application
    app_name: str = "SiteSage"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS - Allow all origins in development
    cors_origins: list = ["*"]

    # Reports
    reports_dir: str = "reports"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()