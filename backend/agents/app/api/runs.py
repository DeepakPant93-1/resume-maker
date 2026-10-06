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

from fastapi import BackgroundTasks, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.api.base import BaseRoutes
from app.core.config import get_settings
from app.core.llm import ModelFactory
from app.core.logging_config import run_context
from app.core.persistence import COMPLETED, FAILED, RUNNING, WAITING_FOR_USER, get_persistence
from app.graph.workflow import ResumeWorkflow

log = logging.getLogger(__name__)


class ResumeRunRequest(BaseModel):
    answer: str = Field(min_length=1, description="The user's answer to the pending question")


class RunRoutes(BaseRoutes):
    """The endpoints under /api/runs: start a run, read it, and answer the question it is waiting on."""

    prefix = "/api/runs"
    tag = "runs"

    # Run-state fields worth exposing on the run record once the graph stops.
    STATE_FIELDS = (
        "job_description", "ats", "gap_analysis", "claims", "needs_user_input", "review", "rewrite_round",
        "ats_with_draft",
    )

    def register(self) -> None:
        self.router.add_api_route("", self.create_run, methods=["POST"], status_code=202)
        self.router.add_api_route("/{run_id}", self.get_run, methods=["GET"])
        self.router.add_api_route("/{run_id}/resume", self.resume_run, methods=["POST"], status_code=202)

    @staticmethod
    def _summarise(result: dict[str, Any]) -> dict[str, Any]:
        return {key: result[key] for key in RunRoutes.STATE_FIELDS if key in result}

    @staticmethod
    def _public(record: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key != "resume"}

    @staticmethod
    def _split_request(body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        """(resume, job_description) from either request shape. A resume never has a top-level "resume" key."""
        if not isinstance(body.get("resume"), dict):
            return body, None
        job_description = body.get("job_description")
        text = job_description.strip() if isinstance(job_description, str) else ""
        return body["resume"], text or None

    @staticmethod
    def _initial_input(job_description: str | None) -> dict[str, Any]:
        return {"job_description_text": job_description}

    def _execute(self, run_id: str, graph_input: Any) -> None:
        """Run (or continue) the graph for `run_id` and record where it stopped."""
        with run_context(run_id):
            self._execute_run(run_id, graph_input)

    def _execute_run(self, run_id: str, graph_input: Any) -> None:
        persistence = get_persistence()
        continuing = isinstance(graph_input, Command)
        started = time.perf_counter()
        log.info("Run %s: %s", "continuing after the user's answer" if continuing else "started", run_id)
        try:
            record = persistence.runs.get(run_id)
            settings = get_settings()
            models = ModelFactory(settings)
            model = models.build_primary()
            fallback = models.build_fallback()
            if fallback is None:
                log.warning("No fallback model; set AGENTS_FALLBACK_MODEL or the other provider's key")
            graph = ResumeWorkflow(record["resume"], model, fallback, persistence.checkpointer,
                                   tier_models=models.build_tier_models()).build()
            result = graph.invoke(
                graph_input,
                config={
                    "configurable": {"thread_id": run_id},
                    "recursion_limit": settings.orchestrator_max_steps,
                },
            )
            state = self._summarise(result)
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

    def create_run(self, body: dict[str, Any], background: BackgroundTasks) -> dict[str, str]:
        resume, job_description = self._split_request(body)
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
        background.add_task(self._execute, run_id, self._initial_input(job_description))
        return {"run_id": run_id, "status": RUNNING}

    def get_run(self, run_id: str) -> dict[str, Any]:
        record = get_persistence().runs.get(run_id)
        if record is None:
            log.warning("GET /api/runs/%s: not found", run_id)
            raise HTTPException(status_code=404, detail="Run not found")
        log.debug("GET /api/runs/%s: %s", run_id, record["status"])  # the UI polls this every 2s, so not INFO
        return self._public(record)

    def resume_run(self, run_id: str, body: ResumeRunRequest, background: BackgroundTasks) -> dict[str, str]:
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
        background.add_task(self._execute, run_id, Command(resume=body.answer))
        return {"run_id": run_id, "status": RUNNING}


router = RunRoutes().router
