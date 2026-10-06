"""Runs API: the Spring backend submits a parsed resume, the LangGraph workflow (app.graph.workflow) works on it.

POST /api/runs takes either the resume JSON itself, or {"resume": {...}, "job_description": "<pasted text>"}.
With a job description, the workflow tailors the resume to it; without one it improves the resume on its own merits.

A run ends `completed` or `failed`, or pauses as `waiting_for_user` when the workflow needs a fact from the user;
answer it with POST /api/runs/{run_id}/resume. Records and graph state persist per `app.core.persistence`.
"""
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.llm import build_chat_model, build_fallback_model
from app.core.logging_config import run_context
from app.core.persistence import COMPLETED, FAILED, RUNNING, WAITING_FOR_USER, get_persistence
from app.graph.workflow import build_workflow

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/runs", tags=["runs"])

# Run-state fields worth exposing on the run record once the graph stops.
_STATE_FIELDS = (
    "job_description", "ats", "gap_analysis", "claims", "needs_user_input", "review", "rewrite_round",
    "ats_with_draft",
)


class ResumeRunRequest(BaseModel):
    answer: str = Field(min_length=1, description="The user's answer to the pending question")


def _summarise(result: dict[str, Any]) -> dict[str, Any]:
    return {key: result[key] for key in _STATE_FIELDS if key in result}


def _public(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "resume"}


def _execute(run_id: str, graph_input: Any) -> None:
    """Run (or continue) the graph for `run_id` and record where it stopped."""
    with run_context(run_id):
        _execute_run(run_id, graph_input)


def _execute_run(run_id: str, graph_input: Any) -> None:
    persistence = get_persistence()
    continuing = isinstance(graph_input, Command)
    started = time.perf_counter()
    log.info("Run %s: %s", "continuing after the user's answer" if continuing else "started", run_id)
    try:
        record = persistence.runs.get(run_id)
        settings = get_settings()
        model = build_chat_model(settings)
        fallback = build_fallback_model(settings)
        if fallback is None:
            log.warning("No fallback model; set AGENTS_FALLBACK_MODEL or the other provider's key")
        graph = build_workflow(record["resume"], model, fallback, persistence.checkpointer)
        result = graph.invoke(
            graph_input,
            config={
                "configurable": {"thread_id": run_id},
                "recursion_limit": settings.orchestrator_max_steps,
            },
        )
        state = _summarise(result)
        seconds = time.perf_counter() - started
        if result.get("__interrupt__"):
            question = result["__interrupt__"][0].value.get("question")
            log.info("Run paused after %.1fs, waiting for the user: %s", seconds, question)
            persistence.runs.update(run_id, status=WAITING_FOR_USER, question=question, state=state)
        else:
            log.info("Run completed in %.1fs", seconds)
            persistence.runs.update(
                run_id, status=COMPLETED, question=None, output=result["output"], state=state
            )
    except Exception as exc:  # noqa: BLE001 - surface any failure on the run record
        log.exception("Run failed after %.1fs", time.perf_counter() - started)
        persistence.runs.update(run_id, status=FAILED, error=str(exc))


def _split_request(body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """(resume, job_description) from either request shape. A resume never has a top-level "resume" key."""
    if not isinstance(body.get("resume"), dict):
        return body, None
    job_description = body.get("job_description")
    text = job_description.strip() if isinstance(job_description, str) else ""
    return body["resume"], text or None


def _initial_input(job_description: str | None) -> dict[str, Any]:
    return {"job_description_text": job_description}


@router.post("", status_code=202)
def create_run(body: dict[str, Any], background: BackgroundTasks) -> dict[str, str]:
    resume, job_description = _split_request(body)
    run_id = uuid.uuid4().hex
    with run_context(run_id):
        log.info("POST /api/runs: resume %s, job description: %s", resume.get("id"),
                 f"{len(job_description)} characters" if job_description else "none")
    get_persistence().runs.create({
        "run_id": run_id,
        "resume_id": resume.get("id"),
        "status": RUNNING,
        "resume": resume,
        "output": None,
        "error": None,
        "question": None,
        "state": {},
    })
    background.add_task(_execute, run_id, _initial_input(job_description))
    return {"run_id": run_id, "status": RUNNING}


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    record = get_persistence().runs.get(run_id)
    if record is None:
        log.warning("GET /api/runs/%s: not found", run_id)
        raise HTTPException(status_code=404, detail="Run not found")
    log.debug("GET /api/runs/%s: %s", run_id, record["status"])  # the UI polls this every 2s, so not INFO
    return _public(record)


@router.post("/{run_id}/resume", status_code=202)
def resume_run(run_id: str, body: ResumeRunRequest, background: BackgroundTasks) -> dict[str, str]:
    """Answer the question a run is waiting on, and let it continue."""
    runs = get_persistence().runs
    record = runs.get(run_id)
    if record is None:
        log.warning("POST /api/runs/%s/resume: run not found", run_id)
        raise HTTPException(status_code=404, detail="Run not found")
    # Atomic, so two quick answers cannot both resume the same pause.
    if not runs.transition(run_id, WAITING_FOR_USER, status=RUNNING, question=None):
        log.warning("POST /api/runs/%s/resume: rejected, run is '%s'", run_id, record["status"])
        raise HTTPException(
            status_code=409, detail=f"Run is '{record['status']}', not waiting for an answer"
        )
    with run_context(run_id):
        log.info("POST /api/runs/%s/resume: answer accepted (%d characters)", run_id, len(body.answer))
    background.add_task(_execute, run_id, Command(resume=body.answer))
    return {"run_id": run_id, "status": RUNNING}
