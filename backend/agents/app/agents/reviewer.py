"""Reviewer agent: fact-checks a draft against the original resume.
"""
import logging
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import SpecialistAgent
from app.agents.result import SpecialistResult
from app.steps.claims import ClaimValidator

log = logging.getLogger(__name__)

REVIEWER_PROMPT = """\
You are the Reviewer on a resume-tailoring team.
Fact-check the draft in the task against the original resume and check ATS formatting
(plain headings, no tables or columns, standard section names).
Reject any claim that has no `[source_ref: ...]`, whose source does not support it, or that
adds employers, dates, metrics or skills absent from the original.
Start your reply with `APPROVED` or `REJECTED`, then list each issue on its own line.
"""


class ReviewerAgent(SpecialistAgent):
    """Fact-checks a draft. Claims without a valid source_ref are rejected in code, before any LLM call."""

    name = "reviewer"
    prompt = REVIEWER_PROMPT

    def __init__(self, *args: Any, validator: ClaimValidator | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.validator = validator or ClaimValidator(self.resume)

    def __call__(self, task: str, state: Mapping[str, Any]) -> SpecialistResult:
        issues = self.validator.validate(state.get("claims") or [])
        if issues:
            log.warning("reviewer: %d claim(s) failed the source_ref check, rejected without a model call", len(issues))
            text = "REJECTED\n" + "\n".join(f"- {issue}" for issue in issues)
            return SpecialistResult(text, {"review": {"approved": False, "issues": issues}})
        text = self._ask([SystemMessage(self._system), HumanMessage(task)])
        approved = text.lstrip().upper().startswith("APPROVED")
        issues = [line.lstrip("-•* ").strip() for line in text.splitlines()[1:] if line.strip()]
        return SpecialistResult(text, {"review": {"approved": approved, "issues": issues}})
