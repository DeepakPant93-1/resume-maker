from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.agents.orchestrator import build_orchestrator
from app.agents.specialists import build_specialists

RESUME = {"profile": {"summary": "Backend engineer"},
          "experience": [{"achievements": "• Cut deploy time 40%"}]}


class Scripted(BaseChatModel):
    """Replies in order; records every message list it was called with."""

    script: list[AIMessage]
    calls: int = 0
    seen: list = []

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "Scripted":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        self.seen.append(messages)
        msg = self.script[self.calls]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _call(name: str, task: str, call_id: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": {"task": task}, "id": call_id}])


def test_rewriter_claims_and_reviewer_verdict_land_in_run_state():
    draft = "Summary\n- Backend engineer who ships [source_ref: profile.summary]"
    specialist_model = Scripted(script=[AIMessage(content=draft), AIMessage(content="APPROVED")], seen=[])
    orchestrator_model = Scripted(script=[
        _call("rewriter", "rewrite summary", "1"),
        _call("reviewer", "check draft", "2"),
        AIMessage(content="Done"),
    ], seen=[])
    graph = build_orchestrator(orchestrator_model, build_specialists(specialist_model, RESUME))

    result = graph.invoke({"messages": [HumanMessage("tailor it")]})

    assert result["claims"] == [{"text": "Backend engineer who ships",
                                 "source_ref": "profile.summary", "section": "Summary"}]
    assert result["review"] == {"approved": True, "issues": []}
    assert result["messages"][-1].content == "Done"


def test_reviewer_rejects_unsourced_claims_without_calling_the_llm():
    draft = "Experience\n- Invented a 10x speedup\n- Cut deploy time 40% [source_ref: experience[0].achievements]"
    specialist_model = Scripted(script=[AIMessage(content=draft)], seen=[])  # a 2nd call would IndexError
    orchestrator_model = Scripted(script=[
        _call("rewriter", "rewrite experience", "1"),
        _call("reviewer", "check draft", "2"),
        AIMessage(content="Needs another round"),
    ], seen=[])
    graph = build_orchestrator(orchestrator_model, build_specialists(specialist_model, RESUME))

    result = graph.invoke({"messages": [HumanMessage("tailor it")]})

    assert specialist_model.calls == 1  # rewriter only
    assert result["review"]["approved"] is False
    assert "no source_ref" in result["review"]["issues"][0]
    assert any("REJECTED" in str(m.content) for m in result["messages"])


def test_a_new_draft_clears_the_stale_review_and_keeps_other_sections():
    first = "Summary\n- Backend engineer [source_ref: profile.summary]"
    second = "Experience\n- Cut deploy time 40% [source_ref: experience[0].achievements]"
    specialist_model = Scripted(script=[AIMessage(content=first), AIMessage(content="APPROVED"),
                                        AIMessage(content=second)], seen=[])
    orchestrator_model = Scripted(script=[
        _call("rewriter", "summary", "1"), _call("reviewer", "check", "2"),
        _call("rewriter", "experience", "3"), AIMessage(content="Done"),
    ], seen=[])
    graph = build_orchestrator(orchestrator_model, build_specialists(specialist_model, RESUME))

    result = graph.invoke({"messages": [HumanMessage("tailor it")]})

    assert [c["section"] for c in result["claims"]] == ["Summary", "Experience"]
    assert result["review"] is None
