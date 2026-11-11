"""Creates the one LLM client the whole backend uses. Model and parameters come from .env."""

from langchain_groq import ChatGroq

from app.config.settings import settings

llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=settings.GROQ_TEMPERATURE,
    timeout=settings.GROQ_TIMEOUT,
    max_retries=settings.GROQ_MAX_RETRIES,
    reasoning_effort=settings.GROQ_REASONING_EFFORT,
)
