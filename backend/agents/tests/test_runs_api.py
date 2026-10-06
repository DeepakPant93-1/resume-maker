import os
import uuid

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.core.config import Settings
from app.core.persistence import FAILED, RUNNING, WAITING_FOR_USER, Persistence, build_persistence
from app.main import app

MONGO_URI = os.environ.get("AGENTS_TEST_MONGODB_URI")  # e.g. mongodb://root:secret@localhost:27017/?authSource=admin
RESUME = {"id": "resume-1", "profile": {"summary": "Backend engineer"}}


class Scripted(BaseChatModel):
    """Replies with the next scripted text on each model call (one per LLM node the workflow runs)."""

    script: list[str]
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        reply = self.script[self.calls]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=reply))])


class Exploding(Scripted):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")


GOOD_DRAFT = "Summary\n- Backend engineer [source_ref: profile.summary]"
NEEDS_INPUT_DRAFT = GOOD_DRAFT + "\nNeeds user input\n- How many engineers did you mentor?"


@pytest.fixture(params=["memory", pytest.param("mongo", marks=pytest.mark.skipif(
    not MONGO_URI, reason="set AGENTS_TEST_MONGODB_URI to run against a real MongoDB"))])
def persistence(request) -> Persistence:
    if request.param == "memory":
        yield build_persistence(Settings(_env_file=None))
        return
    database = f"agents_test_{uuid.uuid4().hex[:8]}"
    built = build_persistence(Settings(_env_file=None, mongodb_uri=MONGO_URI, mongodb_database=database))
    yield built
    built.runs._runs.database.client.drop_database(database)


@pytest.fixture
def client(persistence, monkeypatch):
    monkeypatch.setattr("app.api.runs.get_persistence", lambda: persistence)
    monkeypatch.setattr("app.api.runs.build_fallback_model", lambda settings: None)
    with TestClient(app) as test_client:
        yield test_client


def _models(monkeypatch, *models: BaseChatModel):
    """Each graph build gets the next model, like a fresh process would build its own."""
    queue = iter(models)
    monkeypatch.setattr("app.api.runs.build_chat_model", lambda settings: next(queue))


def test_run_completes_and_hides_the_resume_payload(client, monkeypatch):
    _models(monkeypatch, Scripted(script=["Gap", GOOD_DRAFT, "APPROVED"]))

    run_id = client.post("/api/runs", json=RESUME).json()["run_id"]
    run = client.get(f"/api/runs/{run_id}").json()

    assert run["status"] == "completed"
    assert "Reviewer: approved" in run["output"]
    assert run["resume_id"] == "resume-1"
    assert run["state"]["review"] == {"approved": True, "issues": []}
    assert "resume" not in run


def test_run_pauses_for_missing_facts_then_resumes_with_a_fresh_graph(client, monkeypatch):
    _models(monkeypatch,
            Scripted(script=["Gap", NEEDS_INPUT_DRAFT]),
            Scripted(script=[GOOD_DRAFT, "APPROVED"]))

    run_id = client.post("/api/runs", json=RESUME).json()["run_id"]
    paused = client.get(f"/api/runs/{run_id}").json()
    assert paused["status"] == WAITING_FOR_USER
    assert "How many engineers did you mentor?" in paused["question"]

    assert client.post(f"/api/runs/{run_id}/resume", json={"answer": "Two"}).status_code == 202
    done = client.get(f"/api/runs/{run_id}").json()

    assert done["status"] == "completed"
    assert "Reviewer: approved" in done["output"]
    assert done["question"] is None


def test_resume_is_rejected_unless_the_run_is_waiting(client, monkeypatch):
    _models(monkeypatch, Scripted(script=["Gap", GOOD_DRAFT, "APPROVED"]))
    run_id = client.post("/api/runs", json=RESUME).json()["run_id"]

    assert client.post(f"/api/runs/{run_id}/resume", json={"answer": "x"}).status_code == 409
    assert client.post("/api/runs/nope/resume", json={"answer": "x"}).status_code == 404
    assert client.get("/api/runs/nope").status_code == 404
    assert client.post(f"/api/runs/{run_id}/resume", json={"answer": ""}).status_code == 422


def test_failed_run_records_the_error(client, monkeypatch):
    _models(monkeypatch, Exploding(script=[]))

    run_id = client.post("/api/runs", json=RESUME).json()["run_id"]
    run = client.get(f"/api/runs/{run_id}").json()

    assert run["status"] == FAILED
    assert "503" in run["error"]


def test_runs_cut_off_by_a_restart_are_marked_failed_on_startup(persistence, monkeypatch):
    persistence.runs.create({"run_id": "stuck", "status": RUNNING, "resume": RESUME})
    persistence.runs.create({"run_id": "paused", "status": WAITING_FOR_USER, "resume": RESUME})
    monkeypatch.setattr("app.api.runs.get_persistence", lambda: persistence)

    with TestClient(app):
        pass

    assert persistence.runs.get("stuck")["status"] == FAILED
    assert "restart" in persistence.runs.get("stuck")["error"]
    assert persistence.runs.get("paused")["status"] == WAITING_FOR_USER  # its state is checkpointed, so it can resume


def test_transition_only_applies_from_the_expected_status(persistence):
    persistence.runs.create({"run_id": "r", "status": WAITING_FOR_USER, "resume": RESUME})

    assert persistence.runs.transition("r", WAITING_FOR_USER, status=RUNNING) is True
    assert persistence.runs.transition("r", WAITING_FOR_USER, status=RUNNING) is False


def test_run_with_a_job_description_tailors_to_it(client, monkeypatch):
    _models(monkeypatch, Scripted(script=["Gap: kafka", GOOD_DRAFT, "APPROVED"]))
    body = {"resume": {**RESUME, "skills": {"languages": ["Python"]}},
            "job_description": "Requirements\n- Python and Kafka"}

    run_id = client.post("/api/runs", json=body).json()["run_id"]
    run = client.get(f"/api/runs/{run_id}").json()

    assert run["status"] == "completed"
    assert run["resume_id"] == "resume-1"
    assert run["state"]["job_description"]["required_skills"] == ["python", "kafka"]
    assert run["state"]["ats"]["components"]["keywords"]["missing"] == ["kafka"]
    assert "Job keywords still missing: kafka." in run["output"]


def test_legacy_body_still_works_and_is_scored_without_a_job(client, monkeypatch):
    _models(monkeypatch, Scripted(script=["Gap", GOOD_DRAFT, "APPROVED"]))

    run_id = client.post("/api/runs", json=RESUME).json()["run_id"]
    state = client.get(f"/api/runs/{run_id}").json()["state"]

    assert state["job_description"] is None
    assert state["ats"]["against_job"] is False
