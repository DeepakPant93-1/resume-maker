"""Chat model factory: picks the provider and models from settings."""
import logging
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from app.core.config import DEFAULT_MODELS, Settings, get_settings

log = logging.getLogger(__name__)


class ModelFactory:
    """Builds the main chat model and its fallback for one `Settings`."""

    # Tasks that may use their own model: tier -> the Settings field that names it.
    TIER_SETTINGS = {"summary": "summary_model", "rewrite": "rewrite_model"}

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @staticmethod
    def message_text(message: BaseMessage) -> str:
        """Plain text of a message. Gemini returns content as a list of parts, Claude as a string."""
        return message.text

    def _override(self, tier: str) -> Optional[str]:
        field = self.TIER_SETTINGS.get(tier)
        return getattr(self.settings, field) if field else None

    def primary_name(self, tier: str = "agent") -> str:
        """Id of the model for `tier`: its own setting if it has one, else `AGENTS_ORCHESTRATOR_MODEL`, else the default."""
        return (self._override(tier) or self.settings.orchestrator_model
                or DEFAULT_MODELS[self.settings.resolved_provider()])

    def fallback_name(self) -> Optional[str]:
        """Id of the fallback model, or None when there is none (see `build_fallback` for the rules)."""
        if self.settings.fallback_model:
            return self.settings.fallback_model
        other = self._other_provider()
        return DEFAULT_MODELS[other] if self._has_key(other) else None

    def build_primary(self, tier: str = "agent") -> BaseChatModel:
        """Build the chat model for the configured provider and `tier` (needs tool-calling support)."""
        provider = self.settings.resolved_provider()
        model = self.primary_name(tier)
        log.info("Model for %s: %s (%s), %d retries, %.0fs timeout", tier, model, provider,
                 self.settings.llm_max_retries, self.settings.llm_timeout_seconds)
        return self._init(provider, model)

    def build_tier_models(self, tiers: tuple[str, ...] = ("rewrite",)) -> dict[str, BaseChatModel]:
        """Models for the given tiers that have their own setting. Tiers without one are left out (use the main model)."""
        return {tier: self.build_primary(tier) for tier in tiers if self._override(tier)}

    def build_fallback(self) -> Optional[BaseChatModel]:
        """Model to switch to when the primary keeps failing (e.g. provider overload), or None if none is available.

        `AGENTS_FALLBACK_MODEL` names another model on the same provider. Otherwise the other provider's default
        model is used, but only if its API key is set.
        """
        provider = self.settings.resolved_provider()
        if self.settings.fallback_model:
            log.info("Fallback model: %s (%s)", self.settings.fallback_model, provider)
            return self._init(provider, self.settings.fallback_model)
        other = self._other_provider()
        if not self._has_key(other):
            return None
        log.info("Fallback model: %s (%s)", DEFAULT_MODELS[other], other)
        return self._init(other, DEFAULT_MODELS[other])

    def _other_provider(self) -> str:
        return "gemini" if self.settings.resolved_provider() == "anthropic" else "anthropic"

    def _has_key(self, provider: str) -> bool:
        key = self.settings.google_api_key if provider == "gemini" else self.settings.anthropic_api_key
        return bool(key)

    def _init(self, provider: str, model: str) -> BaseChatModel:
        limits = {"timeout": self.settings.llm_timeout_seconds, "max_retries": self.settings.llm_max_retries}
        if provider == "anthropic":
            return init_chat_model(
                model, model_provider="anthropic", api_key=self.settings.anthropic_api_key, **limits
            )
        return init_chat_model(
            model, model_provider="google_genai", api_key=self.settings.google_api_key, **limits
        )
