"""Shared state for one orchestrator run.

The Orchestrator's message history is the base; the specialists add structured results next to it so
later steps (and the API) read facts from state instead of re-parsing chat text. Everything here is
JSON-serialisable so the checkpointer can persist it.
"""
import operator
from typing import Annotated, Any, NotRequired, TypedDict

from langchain.agents import AgentState


class RunState(AgentState):
    # Structured target job (see app.steps.jd) and the latest ATS report (see app.steps.ats).
    job_description: NotRequired[dict[str, Any] | None]
    ats: NotRequired[dict[str, Any]]
    gap_analysis: NotRequired[str]
    # Rewritten statements: {"text", "source_ref", "section"}. Replaced per section on each new draft.
    claims: NotRequired[list[dict[str, Any]]]
    # Facts the Rewriter could not source and needs from the user.
    needs_user_input: NotRequired[list[str]]
    # Latest Reviewer verdict: {"approved": bool, "issues": [str]}; None once a newer draft makes it stale.
    review: NotRequired[dict[str, Any] | None]


class WorkflowState(TypedDict, total=False):
    """State of the fixed resume-tailoring workflow (see app.graph.workflow).

    Every node reads what it needs from here and returns only the fields it changes. A field with no
    reducer is overwritten by the latest write; `user_answers` has one, so each answer is appended.
    """

    # Input: the pasted job description, if any.
    job_description_text: str | None
    # analyze_job: the structured job and the baseline ATS report for the original resume.
    job_description: dict[str, Any] | None
    ats: dict[str, Any]
    # gap_analyst
    gap_analysis: str
    # rewriter: claims carry their source_ref; needs_user_input lists facts it could not source.
    claims: list[dict[str, Any]]
    needs_user_input: list[str]
    rewrite_round: int
    # ask_user: each answered question, appended in order.
    user_answers: Annotated[list[str], operator.add]
    questions_asked: int
    # reviewer: {"approved": bool, "issues": [str]}; None while a fresh draft is unreviewed.
    review: dict[str, Any] | None
    # finalize
    ats_with_draft: dict[str, Any]
    output: str
