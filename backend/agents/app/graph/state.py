"""Shared state for one run of the resume-tailoring workflow.

Everything here is JSON-serialisable so the checkpointer can persist it.
"""
import operator
from typing import Annotated, Any, TypedDict


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
    # rewriter: needs_user_input lists facts it lacks.
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
