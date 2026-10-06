from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.agents.orchestrator import SPECIALISTS, build_orchestrator
from app.agents.specialists import _job_block
from app.steps.jd import extract_jd
from app.tools.resume_tools import build_step_tools

RESUME = {
    "profile": {"full_name": "A", "email": "a@x.io", "phone": "1", "summary": "Python dev"},
    "experience": [{"achievements": "• Cut costs 30% with Docker"}],
    "education": [{"degree": "B.Tech"}],
    "skills": {"languages": ["Python"], "frameworks": [], "tools": ["Docker"]},
}
JD_TEXT = "Requirements\n- Python, Docker and Kafka"


class Scripted(BaseChatModel):
    script: list[AIMessage]
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "Scripted":
        return self

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        msg = self.script[self.calls]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def _call(name: str, args: dict, call_id: str) -> AIMessage:
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def _graph(*script: AIMessage):
    runners = {n: (lambda task, state: "ok") for n in SPECIALISTS}
    return build_orchestrator(Scripted(script=list(script)), runners, extra_tools=build_step_tools(RESUME))


def test_extract_jd_tool_saves_the_job_and_rescoring_to_state():
    graph = _graph(_call("extract_jd", {"text": JD_TEXT}, "1"), AIMessage(content="Done"))

    result = graph.invoke({"messages": [HumanMessage("here is the job")]})

    assert result["job_description"]["required_skills"] == ["python", "docker", "kafka"]
    assert result["ats"]["against_job"] is True
    assert result["ats"]["components"]["keywords"]["missing"] == ["kafka"]
    tool_reply = next(m for m in result["messages"] if m.type == "tool").content
    assert "Required skills: python, docker, kafka" in tool_reply and "ATS score:" in tool_reply


def test_ats_score_tool_can_include_the_draft_claims():
    claims = [{"text": "Built Kafka pipelines", "source_ref": "x", "section": "Experience"}]
    graph = _graph(_call("ats_score", {}, "1"), _call("ats_score", {"include_draft": True}, "2"),
                   AIMessage(content="Done"))

    result = graph.invoke({"messages": [HumanMessage("score it")], "job_description": extract_jd(JD_TEXT),
                           "claims": claims})
    replies = [m.content for m in result["messages"] if m.type == "tool"]

    assert "keywords: 33.3/50" in replies[0]   # python + docker of three
    assert "keywords: 50.0/50" in replies[1]   # the draft adds kafka
    assert result["ats"]["score"] > 90


def test_specialists_receive_the_structured_job_and_missing_keywords():
    from app.steps.ats import ats_score

    jd = extract_jd(JD_TEXT)
    block = _job_block({"job_description": jd, "ats": ats_score(RESUME, jd)})

    assert "Required skills: python, docker, kafka" in block
    assert "Keywords the resume lacks (add only if the resume supports them): kafka" in block
    assert _job_block({}) == ""
