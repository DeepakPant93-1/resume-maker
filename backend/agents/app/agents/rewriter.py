"""Rewriter agent: rewrites resume sections for the target role.
"""
from collections.abc import Mapping
from typing import Any

from app.agents.base import SpecialistAgent
from app.agents.result import SpecialistResult
from app.steps.claims import merge_claims, parse_claims

REWRITER_PROMPT = """\
You are the Rewriter on a resume-tailoring team.
Rewrite only the section(s) named in the task, tailored to the target role.
Put each rewritten claim on its own bullet line, ending with `[source_ref: <path into the resume JSON>]`,
for example `- Led migration to microservices, cutting deploy time 40% [source_ref: experience[0].achievements]`.
The path must exist in the original resume. Put a plain heading line (e.g. `Experience`) before each section's claims.
If you cannot point to a source for a claim, leave it out and list it as a bullet under a
`Needs user input` heading instead.
"""


class RewriterAgent(SpecialistAgent):
    """Rewrites resume sections; every claim carries a source_ref."""

    name = "rewriter"
    prompt = REWRITER_PROMPT

    def handle(self, text: str, state: Mapping[str, Any]) -> SpecialistResult:
        claims, needs_input = parse_claims(text)
        return SpecialistResult(text, {
            "claims": merge_claims(state.get("claims") or [], claims),
            "needs_user_input": needs_input,
            "review": None,  # any earlier verdict was for an older draft
        })
