from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.persistence import build_persistence
from app.main import app

RESUME = {
    "id": "r1",
    "profile": {"full_name": "A", "email": "a@x.io", "phone": "1", "summary": "Backend engineer with Python."},
    "experience": [{"achievements": "• Cut deploy time 40% with Docker"}],
    "education": [{"degree": "B.Tech"}],
    "skills": {"languages": ["Python"], "frameworks": [], "tools": ["Docker"]},
}


def _client(monkeypatch):
    persistence = build_persistence(Settings(_env_file=None))
    monkeypatch.setattr("app.api.runs.get_persistence", lambda: persistence)
    return TestClient(app)


def test_scores_a_resume_without_a_job(monkeypatch):
    with _client(monkeypatch) as client:
        report = client.post("/api/ats", json={"resume": RESUME}).json()

    assert report["against_job"] is False
    assert set(report["components"]) == {"completeness", "impact", "readability"}
    assert 0 < report["score"] <= 100


def test_scores_keyword_match_when_given_a_job_description(monkeypatch):
    body = {"resume": RESUME, "job_description": "Requirements\n- Python, Docker and Kafka"}

    with _client(monkeypatch) as client:
        report = client.post("/api/ats", json=body).json()

    assert report["against_job"] is True
    assert report["components"]["keywords"]["missing"] == ["kafka"]


def test_a_blank_job_description_counts_as_none(monkeypatch):
    with _client(monkeypatch) as client:
        report = client.post("/api/ats", json={"resume": RESUME, "job_description": "   "}).json()

    assert report["against_job"] is False


def test_the_resume_is_required(monkeypatch):
    with _client(monkeypatch) as client:
        assert client.post("/api/ats", json={}).status_code == 422
