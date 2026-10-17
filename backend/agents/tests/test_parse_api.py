import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.main import app

TEXT = """Asha Rao
Java Developer
asha@example.com
Experience
Backend Developer  Acme Corp  Jan 2021 - Present
• Cut deploy time by 40%
• Moved billing to Spring Boot
Skills
Languages: Java, Python
Languages
English - Fluent
"""

REPLY = {
    "profile": {"full_name": "Asha Rao", "job_title": "Java Developer", "email": "asha@example.com"},
    "experience": [{
        "job_title": "Backend Developer", "company": "Acme Corp", "start_date": "Jan 2021", "end_date": "Present",
        "current": True, "achievements": "• Cut deploy time by 40%\n• Moved billing to Spring Boot",
    }],
    "skills": {"languages": ["Java", "Python"], "frameworks": [], "tools": []},
    "spoken_languages": [{"language": "English", "proficiency": "Fluent"}],
}


class Recording(BaseChatModel):
    """Replies with a fixed text and records the messages it was given."""

    reply: str = ""
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
def use_model(monkeypatch):
    def install(reply: str) -> Recording:
        fake = Recording(reply=reply, seen=[])
        monkeypatch.setattr("app.api.parse.ModelFactory.build_primary", lambda self, tier="agent": fake)
        monkeypatch.setattr("app.api.parse.ModelFactory.build_fallback", lambda self: None)
        return fake

    return install


def post(text: str = TEXT):
    return TestClient(app).post("/api/parse", json={"text": text})


def test_returns_the_resume_in_the_java_shape(use_model):
    model = use_model(json.dumps(REPLY))

    response = post()

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["full_name"] == "Asha Rao"
    assert body["profile"]["phone"] is None
    assert body["experience"][0]["current"] is True
    assert body["experience"][0]["achievements"] == "• Cut deploy time by 40%\n• Moved billing to Spring Boot"
    assert body["skills"] == {"languages": ["Java", "Python"], "frameworks": [], "tools": []}
    assert body["spoken_languages"] == [{"language": "English", "proficiency": "Fluent"}]
    assert set(body) == {"profile", "experience", "education", "skills", "projects", "certifications",
                         "spoken_languages"}  # no metadata
    assert "Asha Rao" in model.seen[0][1].content  # the text goes in as data


def test_tolerates_a_code_fence_around_the_json(use_model):
    use_model("```json\n" + json.dumps(REPLY) + "\n```")

    assert post().json()["profile"]["full_name"] == "Asha Rao"


def test_drops_values_that_are_not_in_the_text(use_model):
    reply = json.loads(json.dumps(REPLY))
    reply["profile"]["job_title"] = "Senior Java Architect"  # reworded by the model
    reply["experience"][0]["achievements"] += "\n• Led a team of 12"  # invented
    reply["skills"]["tools"] = ["Kubernetes"]  # invented
    use_model(json.dumps(reply))

    body = post().json()

    assert body["profile"]["job_title"] is None
    assert body["experience"][0]["achievements"] == "• Cut deploy time by 40%\n• Moved billing to Spring Boot"
    assert body["skills"]["tools"] == []
    assert body["profile"]["full_name"] == "Asha Rao"  # real values stay


def test_a_reply_that_is_not_json_is_a_502(use_model):
    use_model("Sorry, I cannot do that")

    assert post().status_code == 502


def test_empty_text_is_a_422_without_a_model_call(use_model):
    model = use_model(json.dumps(REPLY))

    assert post("   ").status_code == 422
    assert model.seen == []


def test_an_unconfigured_model_is_a_503(monkeypatch):
    def not_configured(self, tier="agent"):
        raise ValueError("no API key")

    monkeypatch.setattr("app.api.parse.ModelFactory.build_primary", not_configured)

    assert post().status_code == 503


def test_tolerates_a_small_models_slips(use_model):
    reply = json.loads(json.dumps(REPLY))
    reply["experience"][0]["achievements"] = ["• Cut deploy time by 40%", "• Moved billing to Spring Boot"]
    reply["experience"][0]["current"] = None
    reply["skills"] = None
    reply["education"] = None
    reply["profile"]["phone"] = None
    use_model(json.dumps(reply))

    body = post().json()

    assert body["experience"][0]["achievements"] == "• Cut deploy time by 40%\n• Moved billing to Spring Boot"
    assert body["experience"][0]["current"] is False
    assert body["skills"] == {"languages": [], "frameworks": [], "tools": []}
    assert body["education"] == []
    assert body["profile"]["phone"] is None


def test_a_reply_with_the_wrong_shape_is_a_502(use_model):
    use_model(json.dumps({"profile": "Asha Rao", "experience": "none"}))

    assert post().status_code == 502
