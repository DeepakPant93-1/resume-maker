"""Service configuration, loaded from environment variables."""
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "gemini": "gemini-3.8-flash"}


class Settings(BaseSettings):
    """Agent service settings.

    Both providers are supported. Set `ANTHROPIC_API_KEY` and/or `GOOGLE_API_KEY`
    (env var or `.env`). With both set, `AGENTS_PROVIDER` picks one; without it,
    Anthropic is used if its key is present, otherwise Gemini.
    """

    model_config = SettingsConfigDict(env_prefix="AGENTS_", env_file=".env", extra="ignore")

    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")

    # "anthropic" or "gemini"; auto-detected from the available key when unset.
    provider: Optional[Literal["anthropic", "gemini"]] = None
    # Model id for the chosen provider; defaults per provider (see DEFAULT_MODELS).
    orchestrator_model: Optional[str] = None
    # Upper bound on graph steps (model call + tool call each count) for one orchestrator run.
    orchestrator_max_steps: int = 25

    def resolved_provider(self) -> str:
        if self.provider:
            return self.provider
        if self.anthropic_api_key:
            return "anthropic"
        if self.google_api_key:
            return "gemini"
        raise ValueError("Set ANTHROPIC_API_KEY or GOOGLE_API_KEY (or AGENTS_PROVIDER).")


def get_settings() -> Settings:
    return Settings()
