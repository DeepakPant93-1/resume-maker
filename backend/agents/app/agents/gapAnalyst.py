"""Gap Analyst agent: compares the resume with the job requirements.
"""
from collections.abc import Mapping
from typing import Any

from app.agents.base import SpecialistAgent
from app.agents.orchestrator import SpecialistResult

GAP_ANALYST_PROMPT = """\
You are the Gap Analyst on a resume-tailoring team.
Compare the resume with the job requirements given in the task. If no job description is
given, assess the resume on its own merits (clarity, impact, missing sections).
Return a concise list of: (1) requirements the resume already covers, (2) weak areas,
(3) missing items, and (4) facts you would need to ask the user for. Do not rewrite anything.
"""


class GapAnalystAgent(SpecialistAgent):
    """Compares the resume with the job requirements."""

    name = "gap_analyst"
    prompt = GAP_ANALYST_PROMPT

    def handle(self, text: str, state: Mapping[str, Any]) -> SpecialistResult:
        return SpecialistResult(text, {"gap_analysis": text})
