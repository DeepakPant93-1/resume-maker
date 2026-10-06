"""Builds the specialist agents (Gap Analyst, Rewriter, Reviewer) the workflow runs."""
from collections.abc import Mapping
from typing import Any

from langchain_core.language_models import BaseChatModel

from app.agents.gap_analyst import GAP_ANALYST_PROMPT, GapAnalystAgent
from app.agents.result import SpecialistRunner
from app.agents.reviewer import REVIEWER_PROMPT, ReviewerAgent
from app.agents.rewriter import REWRITER_PROMPT, RewriterAgent

PROMPTS: Mapping[str, str] = {
    GapAnalystAgent.name: GAP_ANALYST_PROMPT,
    RewriterAgent.name: REWRITER_PROMPT,
    ReviewerAgent.name: REVIEWER_PROMPT,
}


def build_specialists(
    model: BaseChatModel, resume: dict[str, Any], fallback: BaseChatModel | None = None
) -> dict[str, SpecialistRunner]:
    """Runners for every specialist the workflow uses, keyed by name."""
    return {
        agent.name: agent(model, resume, fallback) for agent in (GapAnalystAgent, RewriterAgent, ReviewerAgent)
    }
