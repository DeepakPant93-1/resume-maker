"""Chat model factory: picks the provider from settings."""
import logging
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from app.core.config import DEFAULT_MODELS, Settings, get_settings


log = logging.getLogger(__name__)


def _init(provider: str, model: str, settings: Settings) -> BaseChatModel:
    from langchain.chat_models import init_chat_model

    limits = {"timeout": settings.llm_timeout_seconds, "max_retries": settings.llm_max_retries}
    if provider == "anthropic":
        return init_chat_model(
            model, model_provider="anthropic", api_key=settings.anthropic_api_key, **limits
        )
    return init_chat_model(
        model, model_provider="google_genai", api_key=settings.google_api_key, **limits
    )


def primary_model_name(settings: Optional[Settings] = None) -> str:
    """Id of the main model: `AGENTS_ORCHESTRATOR_MODEL`, else the provider's default (see DEFAULT_MODELS)."""
    settings = settings or get_settings()
    return settings.orchestrator_model or DEFAULT_MODELS[settings.resolved_provider()]


def fallback_model_name(settings: Optional[Settings] = None) -> Optional[str]:
    """Id of the fallback model, or None when there is none (see build_fallback_model for the rules)."""
    settings = settings or get_settings()
    if settings.fallback_model:
        return settings.fallback_model
    other = "gemini" if settings.resolved_provider() == "anthropic" else "anthropic"
    other_key = settings.google_api_key if other == "gemini" else settings.anthropic_api_key
    return DEFAULT_MODELS[other] if other_key else None


def build_chat_model(settings: Optional[Settings] = None) -> BaseChatModel:
    """Build the chat model for the configured provider (needs tool-calling support)."""
    settings = settings or get_settings()
    provider = settings.resolved_provider()
    model = primary_model_name(settings)
    log.info("Model: %s (%s), %d retries, %.0fs timeout", model, provider, settings.llm_max_retries,
             settings.llm_timeout_seconds)
    return _init(provider, model, settings)


def build_fallback_model(settings: Optional[Settings] = None) -> Optional[BaseChatModel]:
    """Model to switch to when the primary keeps failing (e.g. provider overload), or None if none is available.

    `AGENTS_FALLBACK_MODEL` names another model on the same provider. Otherwise the other provider's default
    model is used, but only if its API key is set.
    """
    settings = settings or get_settings()
    provider = settings.resolved_provider()
    if settings.fallback_model:
        log.info("Fallback model: %s (%s)", settings.fallback_model, provider)
        return _init(provider, settings.fallback_model, settings)
    other = "gemini" if provider == "anthropic" else "anthropic"
    other_key = settings.google_api_key if other == "gemini" else settings.anthropic_api_key
    if not other_key:
        return None
    log.info("Fallback model: %s (%s)", DEFAULT_MODELS[other], other)
    return _init(other, DEFAULT_MODELS[other], settings)


def message_text(message: BaseMessage) -> str:
    """Plain text of a message. Gemini returns content as a list of parts, Claude as a string."""
    return message.text
