from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.main import app

RESUME = {
    "profile": {"full_name": "A", "job_title": "Java Developer", "summary": ""},
    "experience": [{"job_title": "Developer", "company": "Acme", "achievements": "• Cut deploy time 40%"}],
    "skills": {"languages": ["Java"], "frameworks": ["Spring Boot"], "tools": []},
}


class Recording(BaseChatModel):
    """Replies with a fixed text and records the messages it was given."""

    reply: str = "  Java developer with Spring Boot experience.  "
    seen: list = []

    @property
    def _llm_type(self) -> str:
        return "recording"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "Recording":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        self.seen.append(messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.reply))])


@pytest.fixture
def model(monkeypatch):
    fake = Recording(seen=[])
    monkeypatch.setattr("app.api.summary.ModelFactory.build_primary", lambda self, tier="agent": fake)
    monkeypatch.setattr("app.api.summary.ModelFactory.build_fallback", lambda self: None)
    return fake


def test_writes_a_new_summary_from_the_resume(model):
    response = TestClient(app).post("/api/summary", json={"resume": RESUME})

    assert response.status_code == 200
    assert response.json() == {"summary": "Java developer with Spring Boot experience."}
    system, human = model.seen[0]
    assert "Spring Boot" in system.content  # the resume is the only source of facts
    assert human.content == "Write the professional summary."


def test_improves_the_existing_summary_when_there_is_one(model):
    response = TestClient(app).post("/api/summary", json={"resume": RESUME, "summary": "I do java stuff"})

    assert response.status_code == 200
    assert model.seen[0][1].content == "Improve this professional summary:\nI do java stuff"


def test_refuses_when_there_is_nothing_to_write_from(model):
    response = TestClient(app).post("/api/summary", json={"resume": {"profile": {"full_name": "A"}}})

    assert response.status_code == 422
    assert "job title" in response.json()["detail"]
    assert model.seen == []  # no model call was made


def test_an_unconfigured_model_is_a_503(monkeypatch):
    def not_configured(self, tier="agent"):
        raise ValueError("no API key")

    monkeypatch.setattr("app.api.summary.ModelFactory.build_primary", not_configured)

    response = TestClient(app).post("/api/summary", json={"resume": RESUME})

    assert response.status_code == 503
