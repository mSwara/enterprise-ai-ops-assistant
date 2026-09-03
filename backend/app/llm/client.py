from langchain_groq import ChatGroq
from app.core.config import settings


def get_llm(temperature: float = 0.2):
    """
    Returns a configured ChatGroq LLM instance with SDK-level retries.
    """
    return ChatGroq(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=temperature,
        max_retries=4,
    )