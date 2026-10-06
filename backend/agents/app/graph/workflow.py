r"""The resume-tailoring workflow, written as an explicit LangGraph `StateGraph`.

    START -> analyze_job -> gap_analyst -> rewriter --(facts missing)--> ask_user --+
                                              ^   \--(otherwise)--> reviewer         |
                                              |                         |            |
                                              +----(rejected, < 3 rounds)           |
                                              +<-------------------------------------+
                                                          (approved or out of rounds) -> finalize -> END

Nodes are plain functions: `state in, changed fields out`. The edges are fixed in code, so the model only
ever runs inside the three specialist nodes. That keeps runs predictable, testable, and cheap in tokens.
The `ask_user` node pauses the graph with `interrupt()`; with a checkpointer it resumes from where it stopped.
"""
import logging
from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt

from app.agents.orchestrator import SpecialistResult
from app.agents.specialists import build_specialists
from app.graph.state import WorkflowState
from app.steps.ats import ats_score
from app.steps.jd import extract_jd

log = logging.getLogger(__name__)

MAX_REWRITE_ROUNDS = 3  # drafts the Rewriter may produce before we stop and report open issues
MAX_QUESTION_ROUNDS = 2  # times the workflow may pause to ask the user for facts


def route_after_rewrite(state: Mapping[str, Any]) -> Literal["ask_user", "reviewer"]:
    """Missing facts go to the user first (a bounded number of times); otherwise the draft is reviewed."""
    if state.get("needs_user_input") and state.get("questions_asked", 0) < MAX_QUESTION_ROUNDS:
        return "ask_user"
    return "reviewer"


def route_after_review(state: Mapping[str, Any]) -> Literal["rewriter", "finalize"]:
    """Approved drafts finish; rejected ones go back to the Rewriter until the round limit."""
    if (state.get("review") or {}).get("approved"):
        return "finalize"
    return "rewriter" if state.get("rewrite_round", 0) < MAX_REWRITE_ROUNDS else "finalize"


def _bullets(items: list[str]) -> str:
    """Format `items` as one "- item" line each, for embedding lists in a prompt or summary."""
    return "\n".join(f"- {item}" for item in items)


def _rewrite_task(state: Mapping[str, Any]) -> str:
    """Task text for the Rewriter: the goal, plus the gap analysis, the user's answers and any reviewer issues so far."""
    goal = "for the target job" if state.get("job_description") else "for clarity and impact"
    parts = [f"Rewrite the Summary and each Experience entry {goal}."]
    if state.get("gap_analysis"):
        parts.append("Gap analysis (data):\n" + state["gap_analysis"])
    if state.get("user_answers"):
        parts.append("Facts the user confirmed (data):\n" + "\n".join(state["user_answers"]))
    review = state.get("review")
    if review and not review.get("approved"):
        parts.append("Fix these issues the reviewer found in your last draft:\n" + _bullets(review["issues"]))
    return "\n\n".join(parts)


def _review_task(state: Mapping[str, Any]) -> str:
    """Task text for the Reviewer: every current claim with its source_ref, to fact-check against the resume."""
    draft = _bullets([f"{c['text']} [source_ref: {c['source_ref']}]" for c in state.get("claims") or []])
    return "Review this draft against the original resume:\n" + draft


def _summary(resume: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    """Closing summary and the ATS report with the new claims counted. Plain code, no model call."""
    claims = state.get("claims") or []
    after = ats_score(resume, state.get("job_description"), "\n".join(c["text"] for c in claims))
    review = state.get("review") or {}
    rounds = state.get("rewrite_round", 0)
    sections = sorted({c["section"] for c in claims if c.get("section")})

    lines = [f"Rewrote {len(claims)} claim(s)" + (f" in: {', '.join(sections)}." if sections else ".")]
    if review.get("approved"):
        lines.append(f"Reviewer: approved after {rounds} draft(s).")
    else:
        lines.append(f"Reviewer: NOT approved after {rounds} draft(s). Open issues:")
        lines += [f"  - {issue}" for issue in review.get("issues") or ["no review was completed"]]
    before = (state.get("ats") or {}).get("score")
    lines.append(f"ATS score: {before} -> {after['score']} (counting the new claims).")
    missing = (after["components"].get("keywords") or {}).get("missing")
    if missing:
        lines.append("Job keywords still missing: " + ", ".join(missing) + ".")
    if state.get("needs_user_input"):
        lines.append("Facts still needed from you:\n" + _bullets(state["needs_user_input"]))
    return "\n".join(lines), after


def build_workflow(
    resume: dict[str, Any],
    model: BaseChatModel,
    fallback: BaseChatModel | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Build the workflow for one resume. `fallback` answers if `model` keeps failing."""
    specialists = build_specialists(model, resume, fallback)

    def update_from(result: "str | SpecialistResult") -> dict[str, Any]:
        """The state fields a specialist wants written (none if it returned plain text)."""
        return result.update if isinstance(result, SpecialistResult) else {}

    def analyze_job(state: WorkflowState) -> dict[str, Any]:
        """Node: structure the job description (if any) and score the original resume. No model call."""
        text = state.get("job_description_text")
        jd = extract_jd(text) if text else None
        report = ats_score(resume, jd)
        job = f"{len(jd['required_skills'])} required / {len(jd['preferred_skills'])} preferred skills" if jd else "none"
        log.info("analyze_job: job description: %s; ATS baseline %s/100", job, report["score"])
        return {"job_description": jd, "ats": report}

    def gap_analyst(state: WorkflowState) -> dict[str, Any]:
        """Node: the Gap Analyst compares the resume with the target job; writes `gap_analysis`."""
        task = "Compare the resume with the target job and list the gaps."
        log.info("gap_analyst: analysing")
        return update_from(specialists["gap_analyst"](task, state))

    def rewriter(state: WorkflowState) -> dict[str, Any]:
        """Node: the Rewriter drafts claims (each with a source_ref) and lists facts it lacks; counts the round."""
        round_number = state.get("rewrite_round", 0) + 1
        log.info("rewriter: drafting (round %d of %d)", round_number, MAX_REWRITE_ROUNDS)
        update = update_from(specialists["rewriter"](_rewrite_task(state), state))
        log.info("rewriter: %d claim(s) in the draft, %d fact(s) needed from the user",
                 len(update.get("claims") or []), len(update.get("needs_user_input") or []))
        return {**update, "rewrite_round": round_number}

    def ask_user(state: WorkflowState) -> dict[str, Any]:
        """Node: pause the run to ask the user for the missing facts, then record their answer.

        `interrupt()` stops the graph here. When the run is resumed, this node starts over and `interrupt()`
        returns the answer, so nothing before it may have side effects.
        """
        question = "I need a few facts before I can finish:\n" + _bullets(state["needs_user_input"])
        answer = interrupt({"type": "question", "question": question})
        # Only reached after the user answers: on resume this node restarts and interrupt() returns the answer.
        log.info("ask_user: answer received (%d characters)", len(str(answer)))
        return {
            "user_answers": [f"Q: {question}\nA: {answer}"],
            "questions_asked": state.get("questions_asked", 0) + 1,
            "needs_user_input": [],
        }

    def reviewer(state: WorkflowState) -> dict[str, Any]:
        """Node: the Reviewer checks the draft. An empty draft, or claims with a bad source_ref, are rejected in code."""
        if not state.get("claims"):
            issue = "The rewriter produced no claims with a source_ref"
            log.warning("reviewer: rejected, the draft has no claims (no model call)")
            return {"review": {"approved": False, "issues": [issue]}}
        update = update_from(specialists["reviewer"](_review_task(state), state))
        review = update.get("review") or {}
        log.info("reviewer: %s, %d issue(s)", "approved" if review.get("approved") else "REJECTED",
                 len(review.get("issues") or []))
        return update

    def finalize(state: WorkflowState) -> dict[str, Any]:
        """Node: write the closing summary (`output`) and the ATS score with the new claims. No model call."""
        output, after = _summary(resume, state)
        approved = (state.get("review") or {}).get("approved")
        log.info("finalize: ATS %s -> %s, reviewer %s after %s draft(s)", (state.get("ats") or {}).get("score"),
                 after["score"], "approved" if approved else "did NOT approve", state.get("rewrite_round", 0))
        return {"output": output, "ats_with_draft": after}

    graph = StateGraph(WorkflowState)
    for name, node in [("analyze_job", analyze_job), ("gap_analyst", gap_analyst), ("rewriter", rewriter),
                       ("ask_user", ask_user), ("reviewer", reviewer), ("finalize", finalize)]:
        graph.add_node(name, node)

    graph.add_edge(START, "analyze_job")
    graph.add_edge("analyze_job", "gap_analyst")
    graph.add_edge("gap_analyst", "rewriter")
    graph.add_conditional_edges("rewriter", route_after_rewrite, ["ask_user", "reviewer"])
    graph.add_edge("ask_user", "rewriter")
    graph.add_conditional_edges("reviewer", route_after_review, ["rewriter", "finalize"])
    graph.add_edge("finalize", END)
    return graph.compile(checkpointer=checkpointer, name="resume_workflow")
