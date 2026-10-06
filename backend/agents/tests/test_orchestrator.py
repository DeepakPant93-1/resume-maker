from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents.orchestrator import SPECIALISTS, build_orchestrator


class ScriptedModel(BaseChatModel):
    """Returns pre-scripted AI messages in order; ignores the input."""

    script: list[AIMessage]
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedModel":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        msg = self.script[self.calls]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _call(name: str, args: dict, call_id: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def _runners(log: list[str]) -> dict:
    return {n: (lambda task, state, n=n: log.append(f"{n}:{task}") or f"{n} done") for n in SPECIALISTS}


def test_delegates_to_specialist_and_returns_final_answer():
    log: list[str] = []
    model = ScriptedModel(script=[_call("gap_analyst", {"task": "compare"}, "1"),
                                  AIMessage(content="All done")])
    graph = build_orchestrator(model, _runners(log))

    result = graph.invoke({"messages": [HumanMessage("tailor my resume")]})

    assert log == ["gap_analyst:compare"]
    assert result["messages"][-1].content == "All done"


def test_ask_user_pauses_and_resumes_with_answer():
    model = ScriptedModel(script=[_call("ask_user", {"question": "How many clusters?"}, "1"),
                                  AIMessage(content="Thanks")])
    graph = build_orchestrator(model, _runners([]), checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "t1"}}

    paused = graph.invoke({"messages": [HumanMessage("go")]}, cfg)
    assert paused["__interrupt__"][0].value["question"] == "How many clusters?"

    resumed = graph.invoke(Command(resume="12 clusters"), cfg)
    assert resumed["messages"][-1].content == "Thanks"
    assert any("12 clusters" in str(m.content) for m in resumed["messages"])


def test_rejects_missing_specialist_runner():
    with pytest.raises(ValueError, match="reviewer"):
        build_orchestrator(ScriptedModel(script=[]), {"gap_analyst": str, "rewriter": str})
