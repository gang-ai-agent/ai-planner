from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Vacation Planner"
    app_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+psycopg://planner:planner@localhost:5432/ai_planner"
    )
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_enabled: bool = False
    qdrant_memory_enabled: bool = False
    qdrant_travel_collection: str = "trips"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str = "ai-vacation-planner"
    llm_enabled: bool = False
    llm_provider: str = "local"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "granite4.1:3b"
    ollama_timeout_seconds: float = 10.0
    embedding_provider: str = "ollama"
    ollama_embedding_model: str = "nomic-embed-text:latest"
    ollama_embedding_timeout_seconds: float = 15.0
    retrieval_query_language: str = "zh"
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    max_user_input_chars: int = 12000
    max_agent_retries: int = 3
    default_embedding_dim: int = 768


@lru_cache
def get_settings() -> Settings:
    return Settings()
