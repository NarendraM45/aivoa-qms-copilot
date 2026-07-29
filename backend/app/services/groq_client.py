"""Centralized Groq/LangChain client factory with retry logic."""
import logging
from langchain_groq import ChatGroq
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _is_rate_limit_error(exception: BaseException) -> bool:
    """Check if an exception is a rate limit error (429)."""
    error_str = str(exception).lower()
    return "429" in error_str or "rate" in error_str or "too many" in error_str


def get_fast_llm() -> ChatGroq:
    """Returns ChatGroq configured for fast tasks (extraction, classification).
    
    Uses GROQ_MODEL_FAST (default: openai/gpt-oss-20b) with low temperature
    for consistent, deterministic extraction results.
    """
    settings = get_settings()
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_FAST,
        temperature=0.1,
        max_retries=3,
    )


def get_reasoning_llm() -> ChatGroq:
    """Returns ChatGroq configured for reasoning tasks (chat, root cause, CAPA).
    
    Uses GROQ_MODEL_REASONING (default: openai/gpt-oss-120b) with moderate
    temperature for nuanced, contextual responses.
    """
    settings = get_settings()
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL_REASONING,
        temperature=0.5,
        max_retries=3,
    )


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception(_is_rate_limit_error),
    reraise=True,
)
async def invoke_with_retry(llm: ChatGroq, messages: list) -> str:
    """Invoke LLM with exponential backoff retry for rate limit errors.
    
    Groq free tier is 8K TPM — during rapid dev/testing this gets hit often.
    Retries up to 5 times with exponential backoff (2s, 4s, 8s, 16s, 30s max).
    """
    try:
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"LLM invocation error: {type(e).__name__}: {e}")
        raise
