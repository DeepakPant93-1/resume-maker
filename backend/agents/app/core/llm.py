"""Chat model factory: picks the provider and models from settings."""
import logging
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from app.core.config import DEFAULT_MODELS, KEYED_PROVIDERS, Settings, get_settings

log = logging.getLogger(__name__)


class ModelFactory:
    """Builds the main chat model and its fallback for one `Settings`."""

    # Tasks that may use their own model: tier -> the Settings field that names it.
    TIER_SETTINGS = {"summary": "summary_model", "rewrite": "rewrite_model", "parse": "parse_model"}

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
        other = self._fallback_provider()
        return DEFAULT_MODELS[other] if other else None

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

        `AGENTS_FALLBACK_MODEL` names another model on the same provider. Otherwise the default model of the first
        other provider with an API key is used (`KEYED_PROVIDERS` order), e.g. Groq when Gemini's quota runs out.
        """
        provider = self.settings.resolved_provider()
        if self.settings.fallback_model:
            log.info("Fallback model: %s (%s)", self.settings.fallback_model, provider)
            return self._init(provider, self.settings.fallback_model)
        other = self._fallback_provider()
        if other is None:
            return None
        log.info("Fallback model: %s (%s)", DEFAULT_MODELS[other], other)
        return self._init(other, DEFAULT_MODELS[other])

    def _fallback_provider(self) -> Optional[str]:
        """First provider other than the primary that has an API key. Ollama is never a silent fallback."""
        primary = self.settings.resolved_provider()
        return next((p for p in KEYED_PROVIDERS if p != primary and self.settings.api_key(p)), None)

    def _init(self, provider: str, model: str) -> BaseChatModel:
        limits = {"timeout": self.settings.llm_timeout_seconds, "max_retries": self.settings.llm_max_retries}
        if provider == "ollama":  # langchain-ollama takes no max_retries
            return init_chat_model(
                model, model_provider="ollama", base_url=self.settings.ollama_base_url,
                client_kwargs={"timeout": self.settings.llm_timeout_seconds},
            )
        if provider == "anthropic":
            return init_chat_model(
                model, model_provider="anthropic", api_key=self.settings.anthropic_api_key, **limits
            )
        if provider == "groq":
            if model.startswith("openai/gpt-oss"):  # other Groq models reject these effort values
                limits["reasoning_effort"] = self.settings.groq_reasoning_effort
            return init_chat_model(model, model_provider="groq", api_key=self.settings.groq_api_key, **limits)
        return init_chat_model(
            model, model_provider="google_genai", api_key=self.settings.google_api_key, **limits
        )
