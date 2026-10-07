"""Reviewer agent: fact-checks the Rewriter's draft against the original resume."""
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import SpecialistAgent
from app.agents.result import SpecialistResult

REVIEWER_PROMPT = """\
You are the Reviewer on a resume-tailoring team.
Fact-check the draft in the task against the original resume and check ATS formatting
(plain headings, no tables or columns, standard section names).
Reject any claim that adds employers, dates, metrics or skills absent from the original.
Start your reply with `APPROVED` or `REJECTED`, then list each issue on its own line.
"""


class ReviewerAgent(SpecialistAgent):
    """Fact-checks a draft against the original resume with the model."""

    name = "reviewer"
    prompt = REVIEWER_PROMPT

    def __call__(self, task: str, state: Mapping[str, Any]) -> SpecialistResult:
        text = self._ask([SystemMessage(self._system), HumanMessage(task)])
        approved = text.lstrip().upper().startswith("APPROVED")
        issues = [line.lstrip("-•* ").strip() for line in text.splitlines()[1:] if line.strip()]
        return SpecialistResult(text, {"review": {"approved": approved, "issues": issues}})
