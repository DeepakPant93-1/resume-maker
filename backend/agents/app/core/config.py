"""Service configuration, loaded from environment variables."""
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "gemini": "gemini-3.8-flash", "ollama": "llama3.2:1b"}


class Settings(BaseSettings):
    """Agent service settings.

    Anthropic, Gemini and a local Ollama server are supported. Set `ANTHROPIC_API_KEY` and/or
    `GOOGLE_API_KEY` (env var or `.env`). With both set, `AGENTS_PROVIDER` picks one; without it,
    Anthropic is used if its key is present, otherwise Gemini. Ollama needs no key: set
    `AGENTS_PROVIDER=ollama` (it is never auto-detected).
    """

    model_config = SettingsConfigDict(env_prefix="AGENTS_", env_file=".env", extra="ignore")

    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")

    # Base URL of the Ollama server (used when the provider is "ollama").
    ollama_base_url: str = "http://localhost:11434"

    # "anthropic", "gemini" or "ollama"; auto-detected from the available key when unset.
    provider: Optional[Literal["anthropic", "gemini", "ollama"]] = None
    # Model id for the chosen provider; defaults per provider (see DEFAULT_MODELS). Used by the Gap Analyst and Reviewer.
    orchestrator_model: Optional[str] = None
    # Optional lighter/cheaper models for simpler tasks. Unset means the model above is used.
    summary_model: Optional[str] = None  # the "Write with AI" summary
    rewrite_model: Optional[str] = None  # the Rewriter
    parse_model: Optional[str] = None  # turning an uploaded resume's text into JSON
    # Upper bound on graph steps (model call + tool call each count) for one workflow run.
    orchestrator_max_steps: int = 25
    # Per-request timeout and retry count for LLM calls, so a stalled call fails instead of hanging.
    llm_timeout_seconds: float = 90
    # The client backs off exponentially between retries, so 5 rides out a short provider overload (HTTP 503).
    llm_max_retries: int = 5
    # Model used when the primary keeps failing. Defaults to the other provider's model when its key is set.
    fallback_model: Optional[str] = None
    # Log level of the service's own loggers: DEBUG, INFO, WARNING...
    log_level: str = "INFO"

    def resolved_provider(self) -> str:
        if self.provider:
            return self.provider
        if self.anthropic_api_key:
            return "anthropic"
        if self.google_api_key:
            return "gemini"
        raise ValueError("Set ANTHROPIC_API_KEY or GOOGLE_API_KEY (or AGENTS_PROVIDER=ollama).")


def get_settings() -> Settings:
    return Settings()
