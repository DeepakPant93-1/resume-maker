"""Chat model factory: picks the provider from settings."""
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from app.core.config import DEFAULT_MODELS, Settings, get_settings


def build_chat_model(settings: Optional[Settings] = None) -> BaseChatModel:
    """Build the chat model for the configured provider (needs tool-calling support)."""
    from langchain.chat_models import init_chat_model

    settings = settings or get_settings()
    provider = settings.resolved_provider()
    model = settings.orchestrator_model or DEFAULT_MODELS[provider]
    if provider == "anthropic":
        return init_chat_model(model, model_provider="anthropic", api_key=settings.anthropic_api_key)
    return init_chat_model(model, model_provider="google_genai", api_key=settings.google_api_key)


def message_text(message: BaseMessage) -> str:
    """Plain text of a message. Gemini returns content as a list of parts, Claude as a string."""
    return message.text
