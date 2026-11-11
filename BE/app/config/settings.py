"""Loads every config value from .env. Code reads settings.X and never hard-codes values."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str
    APP_VERSION: str

    # Groq (hosted LLM)
    GROQ_API_KEY: SecretStr
    GROQ_MODEL: str
    GROQ_TEMPERATURE: float
    GROQ_TIMEOUT: int
    GROQ_MAX_RETRIES: int
    GROQ_REASONING_EFFORT: str

    # MongoDB Atlas
    MONGODB_URI: SecretStr
    MONGODB_DB: str

    # Ticket rules
    SLA_HOURS: dict[str, int]
    SIMILAR_TICKETS_LIMIT: int

    # Agent
    AGENT_RETRY_ATTEMPTS: int

    # Pinecone (vector DB, hosted embedding + rerank models)
    PINECONE_API_KEY: SecretStr
    PINECONE_INDEX: str
    PINECONE_CLOUD: str
    PINECONE_REGION: str
    PINECONE_EMBED_MODEL: str
    PINECONE_EMBED_DIMENSION: int
    PINECONE_RERANK_MODEL: str

    # RAG
    RAG_KB_DIR: str
    RAG_CHUNK_SIZE: int
    RAG_CHUNK_OVERLAP: int
    RAG_TOP_K: int
    RAG_TOP_N: int


settings = Settings()
