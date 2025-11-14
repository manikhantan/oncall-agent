"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    host: str = "0.0.0.0"

    # GCP Configuration
    gcp_project_id: str | None = None
    gcp_credentials_json: str | None = None  # Path to credentials file or JSON string
    gcp_log_filter: str = ""  # Cloud Logging filter query
    gcp_log_limit: int = 100  # Number of logs to fetch per request

    # AI/LLM Configuration
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = "gpt-4"  # Model to use for analysis
    llm_temperature: float = 0.7

    # Analysis Configuration
    analysis_output_dir: str = "analysis_reports"
    max_log_entries_to_analyze: int = 50


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
