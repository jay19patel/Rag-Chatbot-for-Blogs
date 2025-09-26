from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for environment variables."""

    # Mistral AI API Key
    MISTRAL_API_KEY: str

    # Optional API Keys
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Database settings
    DATABASE_URL: Optional[str] = "sqlite:///./blogs.db"

    # App settings
    DEBUG: bool = False
    APP_NAME: str = "AI Chatbot"
    VERSION: str = "1.0.0"

    # Model settings
    DEFAULT_MODEL: str = "mistral-small"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()