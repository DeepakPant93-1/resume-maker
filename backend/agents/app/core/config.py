"""Service configuration, loaded from environment variables."""
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODELS = {"anthropic": "claude-sonnet-5-5", "gemini": "gemini-3.8-flash", "groq": "openai/gpt-oss-120b",
                  "ollama": "llama3.2:1b"}
# Providers that need an API key, in the order they are auto-detected and tried as the fallback.
KEYED_PROVIDERS = ("anthropic", "gemini", "groq")


class Settings(BaseSettings):
    """Agent service settings.

    Anthropic, Gemini, Groq and a local Ollama server are supported. Set `ANTHROPIC_API_KEY`,
    `GOOGLE_API_KEY` and/or `GROQ_API_KEY` (env var or `.env`). With several set, `AGENTS_PROVIDER`
    picks one; without it, the first with a key in `KEYED_PROVIDERS` order is used. Ollama needs no
    key: set `AGENTS_PROVIDER=ollama` (it is never auto-detected).
    """

    model_config = SettingsConfigDict(env_prefix="AGENTS_", env_file=".env", extra="ignore")

    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, validation_alias="GROQ_API_KEY")

    # Base URL of the Ollama server (used when the provider is "ollama").
    ollama_base_url: str = "http://localhost:11434"

    # "anthropic", "gemini", "groq" or "ollama"; auto-detected from the available key when unset.
    provider: Optional[Literal["anthropic", "gemini", "groq", "ollama"]] = None
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
    # Reasoning effort for Groq's gpt-oss models ("low", "medium", "high"). Their thinking counts against the output
    # limit, so at higher effort long replies (a parsed resume, a rewrite) get cut off before the answer is complete.
    groq_reasoning_effort: str = "low"
    # Model used when the primary keeps failing. Defaults to the next keyed provider's model (see KEYED_PROVIDERS).
    fallback_model: Optional[str] = None
    # Log level of the service's own loggers: DEBUG, INFO, WARNING...
    log_level: str = "INFO"

    def api_key(self, provider: str) -> Optional[str]:
        """The API key for `provider`, or None (Ollama has none)."""
        return {"anthropic": self.anthropic_api_key, "gemini": self.google_api_key,
                "groq": self.groq_api_key}.get(provider)

    def resolved_provider(self) -> str:
        if self.provider:
            return self.provider
        for provider in KEYED_PROVIDERS:
            if self.api_key(provider):
                return provider
        raise ValueError("Set ANTHROPIC_API_KEY, GOOGLE_API_KEY or GROQ_API_KEY (or AGENTS_PROVIDER=ollama).")


def get_settings() -> Settings:
    return Settings()
