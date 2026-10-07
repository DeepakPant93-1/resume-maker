from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.agents.specialists import SpecialistTeam
from app.core.config import Settings
from app.core.llm import ModelFactory


class OverloadedModel(BaseChatModel):
    """Always fails like Gemini does under load (HTTP 503)."""

    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "overloaded"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "OverloadedModel":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        self.calls += 1
        raise RuntimeError("503 UNAVAILABLE: This model is currently experiencing high demand.")


class HealthyModel(BaseChatModel):
    reply: str = "FROM FALLBACK"

    @property
    def _llm_type(self) -> str:
        return "healthy"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "HealthyModel":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.reply))])


@pytest.fixture(autouse=True)
def _no_ambient_keys(monkeypatch):
    for key in ("ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "AGENTS_PROVIDER", "AGENTS_FALLBACK_MODEL"):
        monkeypatch.delenv(key, raising=False)


def _settings(**values) -> Settings:
    return Settings(_env_file=None, **values)


def test_no_fallback_when_only_one_provider_key_is_set():
    assert ModelFactory(_settings(GOOGLE_API_KEY="g-key")).build_fallback() is None


def test_fallback_is_the_other_provider_when_its_key_is_set():
    fallback = ModelFactory(_settings(GOOGLE_API_KEY="g-key", ANTHROPIC_API_KEY="a-key", provider="gemini")).build_fallback()
    assert type(fallback).__name__ == "ChatAnthropic"


def test_fallback_model_setting_uses_same_provider():
    fallback = ModelFactory(_settings(GOOGLE_API_KEY="g-key", fallback_model="gemini-2.5-flash")).build_fallback()
    assert type(fallback).__name__ == "ChatGoogleGenerativeAI"
    assert fallback.model.endswith("gemini-2.5-flash")


def test_retries_default_rides_out_a_short_overload():
    assert _settings(GOOGLE_API_KEY="g-key").llm_max_retries >= 5


def test_specialist_uses_fallback_when_primary_is_overloaded():
    primary, fallback = OverloadedModel(), HealthyModel()
    runners = SpecialistTeam(primary, {"id": "r1"}, fallback)

    assert runners["reviewer"]("check", {}).text == "FROM FALLBACK"
    assert primary.calls == 1
