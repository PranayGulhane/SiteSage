"""Application configuration settings."""
import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", 
            os.getenv(
                "DATABASE_URL",
                "postgresql://neondb_owner:npg_ZPzfCTGgrR76@ep-icy-truth-afcxozd7.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
            )
        )
    )

    # Groq AI
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = "llama-3.3-70b-versatile"

    # Application
    app_name: str = "SiteSage"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS
    cors_origins: list = ["http://localhost:5000", "http://127.0.0.1:5000"]

    # Reports
    reports_dir: str = "reports"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()