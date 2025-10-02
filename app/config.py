from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for environment variables."""

    # Mistral AI API Key
    MISTRAL_API_KEY: str
    MONGO_URI: str
    DB_NAME: str = "ai_chatbot"
    COLLECTION_NAME: str = "documents"
    ATLAS_VECTOR_SEARCH_INDEX_NAME: str = "vector_index"

    # App settings
    DEBUG: bool = False
    APP_NAME: str = "AI Chatbot"
    VERSION: str = "1.0.0"

    # Security settings
    BLOG_SAVE_PIN: str = "1234"  # Default PIN, can be overridden in .env

    # Memory settings
    ENABLE_MEMORY: bool = True  # Enable/disable conversation memory
    MEMORY_TYPE: str = "buffer"  # Types: buffer, summary, token_buffer, window
    MEMORY_MAX_TOKEN_LIMIT: int = 2000  # For token_buffer memory
    MEMORY_WINDOW_SIZE: int = 10  # For window memory (number of exchanges)

    # Model settings
    DEFAULT_MODEL: str = "mistral-large-latest"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()