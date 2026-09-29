import logging
from typing import Type, TypeVar
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError
from pydantic import BaseModel

from .config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key or settings.gemini_api_key.strip() in ("", "your_gemini_api_key_here"):
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Please add a valid Gemini API key to your .env file."
        )
    return genai.Client(api_key=settings.gemini_api_key.strip())


def _format_gemini_error(exc: Exception, model_name: str) -> str:
    """Format known Gemini API exceptions into clear, friendly error messages."""
    err_str = str(exc)
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    
    # Check for 404 / Model not found or deprecated
    if code == 404 or "404" in err_str or "NOT_FOUND" in err_str or "not found" in err_str.lower():
        return (
            f"The configured Gemini model '{model_name}' is not available or has been deprecated for your account. "
            f"Please update GEMINI_OUTLINE_MODEL / GEMINI_STORY_MODEL in your .env file (e.g., to 'gemini-3.8-flash')."
        )
    # Check for 429 / Quota / Resource exhausted
    if code == 429 or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
        return (
            f"Gemini API quota exceeded or rate limit reached for model '{model_name}'. "
            "Please check your plan limits or wait a few moments before trying again."
        )
    # Check for 503 / 500 / Overloaded
    if code in (500, 502, 503, 504) or "503" in err_str or "UNAVAILABLE" in err_str or "overloaded" in err_str.lower():
        return (
            f"The Gemini model service ('{model_name}') is temporarily overloaded or unavailable. "
            "Please try again shortly."
        )
    # Check for 400 / 401 / 403
    if code in (401, 403) or "API_KEY_INVALID" in err_str or "PERMISSION_DENIED" in err_str or "invalid api key" in err_str.lower():
        return (
            "Invalid or unauthorized GEMINI_API_KEY. Please check that your API key in .env is correct and active."
        )
    
    return f"Gemini generation error with model '{model_name}': {err_str}"


def generate_structured(model: str, prompt: str, schema: Type[T]) -> T:
    """
    Generate structured JSON output using Gemini with automatic fallback to secondary models
    if the primary configured model is not found or unavailable.
    """
    settings = get_settings()
    client = get_client()

    candidate_models = [model]
    for fallback in settings.gemini_fallback_models:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    last_error: Exception | None = None
    last_friendly_message = ""

    for candidate in candidate_models:
        try:
            logger.info("Calling Gemini structured output with model: %s", candidate)
            response = client.models.generate_content(
                model=candidate,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )

            if getattr(response, "parsed", None) is not None:
                return response.parsed

            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError(f"Gemini model '{candidate}' returned an empty response.")

            return schema.model_validate_json(text)

        except (APIError, ClientError, ServerError, Exception) as exc:
            friendly_msg = _format_gemini_error(exc, candidate)
            logger.warning("Gemini model %s failed: %s", candidate, friendly_msg)
            last_error = exc
            last_friendly_message = friendly_msg

            # If it's an auth error (401/403) or missing key, fallback won't help. Raise immediately.
            code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            if code in (401, 403) or "API_KEY_INVALID" in str(exc) or "PERMISSION_DENIED" in str(exc):
                raise RuntimeError(friendly_msg) from exc

            # If it's 404 or 503, try next fallback candidate
            continue

    raise RuntimeError(last_friendly_message or f"Failed to generate content: {last_error}")
