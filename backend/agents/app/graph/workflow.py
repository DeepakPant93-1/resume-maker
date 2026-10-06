r"""The resume-tailoring workflow, written as an explicit LangGraph `StateGraph`.

    START -> analyze_job -> gap_analyst -> rewriter --(facts missing)--> ask_user --+
                                              ^   \--(otherwise)--> reviewer         |
                                              |                         |            |
                                              +----(rejected, < 3 rounds)           |
                                              +<-------------------------------------+
                                                          (approved or out of rounds) -> finalize -> END

`ResumeWorkflow` owns one run's resume, specialists, job extractor and ATS scorer. Its nodes are methods:
`state in, changed fields out`. The edges are fixed in code, so the model only ever runs inside the three
specialist nodes. That keeps runs predictable, testable, and cheap in tokens.
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

from app.agents.result import SpecialistResult
from app.agents.specialists import SpecialistTeam
from app.graph.state import WorkflowState
from app.steps.ats import AtsScorer
from app.steps.jd import JobDescriptionExtractor

log = logging.getLogger(__name__)


class ResumeWorkflow:
    """One tailoring run for one resume. `build()` returns the compiled LangGraph."""

    MAX_REWRITE_ROUNDS = 3  # drafts the Rewriter may produce before we stop and report open issues
    MAX_QUESTION_ROUNDS = 2  # times the workflow may pause to ask the user for facts

    def __init__(
        self,
        resume: dict[str, Any],
        model: BaseChatModel,
        fallback: BaseChatModel | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
        extractor: JobDescriptionExtractor | None = None,
        scorer: AtsScorer | None = None,
        tier_models: Mapping[str, BaseChatModel] | None = None,
    ) -> None:
        """`fallback` answers if `model` keeps failing. `tier_models` gives some agents their own model."""
        self.resume = resume
        self.checkpointer = checkpointer
        self.extractor = extractor or JobDescriptionExtractor()
        self.scorer = scorer or AtsScorer()
        self.specialists = SpecialistTeam(model, resume, fallback, tier_models)

    # ---- nodes: each takes the state and returns only the fields it changed ----

    def analyze_job(self, state: WorkflowState) -> dict[str, Any]:
        """Node: structure the job description (if any) and score the original resume. No model call."""
        text = state.get("job_description_text")
        jd = self.extractor.extract(text) if text else None
        report = self.scorer.score(self.resume, jd)
        job = f"{len(jd['required_skills'])} required / {len(jd['preferred_skills'])} preferred skills" if jd else "none"
        log.info("analyze_job: job description: %s; ATS baseline %s/100", job, report["score"])
        return {"job_description": jd, "ats": report}

    def gap_analyst(self, state: WorkflowState) -> dict[str, Any]:
        """Node: the Gap Analyst compares the resume with the target job; writes `gap_analysis`."""
        task = "Compare the resume with the target job and list the gaps."
        log.info("gap_analyst: analysing")
        return self._update_from(self.specialists["gap_analyst"](task, state))

    def rewriter(self, state: WorkflowState) -> dict[str, Any]:
        """Node: the Rewriter drafts claims (each with a source_ref) and lists facts it lacks; counts the round."""
        round_number = state.get("rewrite_round", 0) + 1
        log.info("rewriter: drafting (round %d of %d)", round_number, self.MAX_REWRITE_ROUNDS)
        update = self._update_from(self.specialists["rewriter"](self._rewrite_task(state), state))
        log.info("rewriter: %d claim(s) in the draft, %d fact(s) needed from the user",
                 len(update.get("claims") or []), len(update.get("needs_user_input") or []))
        return {**update, "rewrite_round": round_number}

    def ask_user(self, state: WorkflowState) -> dict[str, Any]:
        """Node: pause the run to ask the user for the missing facts, then record their answer.

        `interrupt()` stops the graph here. When the run is resumed, this node starts over and `interrupt()`
        returns the answer, so nothing before it may have side effects.
        """
        question = "I need a few facts before I can finish:\n" + self._bullets(state["needs_user_input"])
        answer = interrupt({"type": "question", "question": question})
        # Only reached after the user answers: on resume this node restarts and interrupt() returns the answer.
        log.info("ask_user: answer received (%d characters)", len(str(answer)))
        return {
            "user_answers": [f"Q: {question}\nA: {answer}"],
            "questions_asked": state.get("questions_asked", 0) + 1,
            "needs_user_input": [],
        }

    def reviewer(self, state: WorkflowState) -> dict[str, Any]:
        """Node: the Reviewer checks the draft. An empty draft, or claims with a bad source_ref, are rejected in code."""
        if not state.get("claims"):
            issue = "The rewriter produced no claims with a source_ref"
            log.warning("reviewer: rejected, the draft has no claims (no model call)")
            return {"review": {"approved": False, "issues": [issue]}}
        update = self._update_from(self.specialists["reviewer"](self._review_task(state), state))
        review = update.get("review") or {}
        log.info("reviewer: %s, %d issue(s)", "approved" if review.get("approved") else "REJECTED",
                 len(review.get("issues") or []))
        return update

    def finalize(self, state: WorkflowState) -> dict[str, Any]:
        """Node: write the closing summary (`output`) and the ATS score with the new claims. No model call."""
        output, after = self._summary(state)
        approved = (state.get("review") or {}).get("approved")
        log.info("finalize: ATS %s -> %s, reviewer %s after %s draft(s)", (state.get("ats") or {}).get("score"),
                 after["score"], "approved" if approved else "did NOT approve", state.get("rewrite_round", 0))
        return {"output": output, "ats_with_draft": after}

    # ---- routing: which node runs next, decided from the state ----

    def after_rewrite(self, state: Mapping[str, Any]) -> Literal["ask_user", "reviewer"]:
        """Missing facts go to the user first (a bounded number of times); otherwise the draft is reviewed."""
        if state.get("needs_user_input") and state.get("questions_asked", 0) < self.MAX_QUESTION_ROUNDS:
            return "ask_user"
        return "reviewer"

    def after_review(self, state: Mapping[str, Any]) -> Literal["rewriter", "finalize"]:
        """Approved drafts finish; rejected ones go back to the Rewriter until the round limit."""
        if (state.get("review") or {}).get("approved"):
            return "finalize"
        return "rewriter" if state.get("rewrite_round", 0) < self.MAX_REWRITE_ROUNDS else "finalize"

    # ---- the graph ----

    def build(self) -> CompiledStateGraph:
        """Wire the nodes and edges and compile the graph."""
        graph = StateGraph(WorkflowState)

        graph.add_node("analyze_job", self.analyze_job)
        graph.add_node("gap_analyst", self.gap_analyst)
        graph.add_node("rewriter", self.rewriter)
        graph.add_node("ask_user", self.ask_user)
        graph.add_node("reviewer", self.reviewer)
        graph.add_node("finalize", self.finalize)

        graph.add_edge(START, "analyze_job")
        graph.add_edge("analyze_job", "gap_analyst")
        graph.add_edge("gap_analyst", "rewriter")
        graph.add_conditional_edges("rewriter", self.after_rewrite, ["ask_user", "reviewer"])
        graph.add_edge("ask_user", "rewriter")
        graph.add_conditional_edges("reviewer", self.after_review, ["rewriter", "finalize"])
        graph.add_edge("finalize", END)

        return graph.compile(checkpointer=self.checkpointer, name="resume_workflow")

    # ---- helpers ----

    @staticmethod
    def _update_from(result: "str | SpecialistResult") -> dict[str, Any]:
        """The state fields a specialist wants written (none if it returned plain text)."""
        return result.update if isinstance(result, SpecialistResult) else {}

    @staticmethod
    def _bullets(items: list[str]) -> str:
        """Format `items` as one "- item" line each, for embedding lists in a prompt or summary."""
        return "\n".join(f"- {item}" for item in items)

    def _rewrite_task(self, state: Mapping[str, Any]) -> str:
        """Task text for the Rewriter: the goal, plus the gap analysis, the user's answers and any reviewer issues."""
        goal = "for the target job" if state.get("job_description") else "for clarity and impact"
        parts = [f"Rewrite the Summary and each Experience entry {goal}."]
        if state.get("gap_analysis"):
            parts.append("Gap analysis (data):\n" + state["gap_analysis"])
        if state.get("user_answers"):
            parts.append("Facts the user confirmed (data):\n" + "\n".join(state["user_answers"]))
        review = state.get("review")
        if review and not review.get("approved"):
            parts.append("Fix these issues the reviewer found in your last draft:\n" + self._bullets(review["issues"]))
        return "\n\n".join(parts)

    def _review_task(self, state: Mapping[str, Any]) -> str:
        """Task text for the Reviewer: every current claim with its source_ref, to fact-check against the resume."""
        draft = self._bullets([f"{c['text']} [source_ref: {c['source_ref']}]" for c in state.get("claims") or []])
        return "Review this draft against the original resume:\n" + draft

    def _summary(self, state: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
        """Closing summary and the ATS report with the new claims counted. Plain code, no model call."""
        claims = state.get("claims") or []
        after = self.scorer.score(self.resume, state.get("job_description"), "\n".join(c["text"] for c in claims))
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
            lines.append("Facts still needed from you:\n" + self._bullets(state["needs_user_input"]))
        return "\n".join(lines), after
