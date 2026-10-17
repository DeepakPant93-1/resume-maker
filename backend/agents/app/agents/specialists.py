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


class SpecialistTeam:
    """The three specialist agents for one resume, looked up by name: `team["rewriter"](task, state)`."""

    AGENTS = (GapAnalystAgent, RewriterAgent, ReviewerAgent)

    def __init__(
        self,
        model: BaseChatModel,
        resume: dict[str, Any],
        fallback: BaseChatModel | None = None,
        tier_models: Mapping[str, BaseChatModel] | None = None,
    ) -> None:
        """`tier_models` gives an agent its own model by tier (e.g. "rewrite"); the others use `model`."""
        tier_models = tier_models or {}
        self.runners: dict[str, SpecialistRunner] = {
            agent.name: agent(tier_models.get(agent.tier, model), resume, fallback) for agent in self.AGENTS
        }

    def __getitem__(self, name: str) -> SpecialistRunner:
        return self.runners[name]
