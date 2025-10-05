"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""  # Optional - for Qdrant Cloud
    qdrant_use_https: bool = False  # Set to True for Qdrant Cloud
    qdrant_collection_name: str = "people_data"
    qdrant_vector_size: int = 1536
    
    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_llm_model: str = "gpt-4o-mini"
    openai_llm_temperature: float = 0.1
    openai_llm_max_tokens: int = 1000
    
    # PostgreSQL Configuration (optional - only needed for name resolution)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "patient_db"
    postgres_user: str = "postgres"
    postgres_password: str = ""  # Optional - only needed if using name resolution
    
    # MongoDB Configuration
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "patient_data"
    
    # Application Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    environment: Literal["development", "staging", "production"] = "development"
    
    # Batch Processing
    embedding_batch_size: int = 32  # Reduced for better reliability
    ingest_batch_size: int = 100
    
    # Retrieval Configuration
    default_top_k: int = 10
    max_top_k: int = 50
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def postgres_dsn(self) -> str:
        """Build PostgreSQL connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Global settings instance
settings = Settings()

