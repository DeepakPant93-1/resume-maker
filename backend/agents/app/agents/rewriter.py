"""Rewriter agent: rewrites resume sections for the target role."""
from collections.abc import Mapping
from typing import Any

from app.agents.base import SpecialistAgent
from app.agents.result import SpecialistResult
from app.steps.claims import ClaimParser

REWRITER_PROMPT = """\
You are the Rewriter on a resume-tailoring team.
Rewrite only the section(s) named in the task, tailored to the target role.
Put each rewritten claim on its own bullet line, for example `- Led migration to microservices, cutting deploy time 40%`.
Put a plain heading line (e.g. `Experience`) before each section's claims.
Use only facts from the original resume. If a claim needs a fact you do not have, leave it out and list it as a
bullet under a `Needs user input` heading instead.
"""


class RewriterAgent(SpecialistAgent):
    """Rewrites resume sections and files each bullet it writes as a claim in the run state."""

    name = "rewriter"
    tier = "rewrite"
    prompt = REWRITER_PROMPT

    def __init__(self, *args: Any, parser: ClaimParser | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.parser = parser or ClaimParser()

    def handle(self, text: str, state: Mapping[str, Any]) -> SpecialistResult:
        claims, needs_input = self.parser.parse(text)
        return SpecialistResult(text, {
            "claims": self.parser.merge(state.get("claims") or [], claims),
            "needs_user_input": needs_input,
            "review": None,  # any earlier verdict was for an older draft
        })
