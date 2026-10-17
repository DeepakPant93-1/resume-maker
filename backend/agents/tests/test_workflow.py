from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.graph.workflow import ResumeWorkflow

MAX_REWRITE_ROUNDS = ResumeWorkflow.MAX_REWRITE_ROUNDS
MAX_QUESTION_ROUNDS = ResumeWorkflow.MAX_QUESTION_ROUNDS

RESUME = {
    "profile": {"full_name": "A", "email": "a@x.io", "phone": "1", "job_title": "Engineer",
                "summary": "Backend engineer"},
    "experience": [{"job_title": "Eng", "company": "Acme", "achievements": "• Cut deploy time 40% with Docker"}],
    "education": [{"degree": "B.Tech"}],
    "skills": {"languages": ["Python"], "frameworks": [], "tools": ["Docker"]},
}
GOOD_DRAFT = ("Summary\n- Backend engineer shipping Python services\n"
              "Experience\n- Cut deploy time 40% using Docker")
INVENTED_DRAFT = "Experience\n- Invented a 10x speedup"
REJECTION = "REJECTED\n- The 10x speedup is not in the original resume"
NEEDS_INPUT_DRAFT = GOOD_DRAFT + "\nNeeds user input\n- How many engineers did you mentor?"


class Scripted(BaseChatModel):
    """Replies in order and records each prompt, so tests can see what a node sent the model."""

    script: list[str]
    calls: int = 0
    seen: list = []

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        self.seen.append(messages)
        reply = self.script[self.calls]  # an IndexError here means the workflow called the model more than expected
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=reply))])

    def prompt(self, call: int) -> str:
        return "\n".join(str(m.content) for m in self.seen[call])


def _run(script: list[str], state: dict[str, Any] | None = None, checkpointer=None, thread="t"):
    model = Scripted(script=script, seen=[])
    graph = ResumeWorkflow(RESUME, model, checkpointer=checkpointer).build()
    config = {"configurable": {"thread_id": thread}}
    return model, graph, graph.invoke(state or {}, config)


def test_happy_path_runs_every_node_once_and_summarises():
    model, _, result = _run(["Gap: none", GOOD_DRAFT, "APPROVED"])

    assert model.calls == 3  # gap analyst, rewriter, reviewer
    assert result["review"] == {"approved": True, "issues": []}
    assert result["rewrite_round"] == 1
    assert [c["section"] for c in result["claims"]] == ["Summary", "Experience"]
    assert "Reviewer: approved after 1 draft(s)." in result["output"]
    assert result["ats_with_draft"]["score"] >= result["ats"]["score"]


def test_a_rejected_draft_is_sent_back_to_the_rewriter_with_the_issue():
    model, _, result = _run(["Gap", INVENTED_DRAFT, REJECTION, GOOD_DRAFT, "APPROVED"])

    assert model.calls == 5  # gap, rewrite, review, rewrite again, review
    assert result["rewrite_round"] == 2
    assert "10x speedup is not in the original" in model.prompt(3)  # the second rewrite was told why
    assert result["review"]["approved"] is True


def test_it_stops_after_the_round_limit_and_reports_open_issues():
    model, _, result = _run(["Gap"] + [INVENTED_DRAFT, REJECTION] * MAX_REWRITE_ROUNDS)

    assert result["rewrite_round"] == MAX_REWRITE_ROUNDS
    assert f"NOT approved after {MAX_REWRITE_ROUNDS} draft(s)" in result["output"]
    assert "10x speedup is not in the original" in result["output"]


def test_a_draft_with_no_claims_is_not_reviewed_by_the_model():
    model, _, result = _run(["Gap"] + ["I could not find anything to rewrite."] * MAX_REWRITE_ROUNDS)

    assert model.calls == 1 + MAX_REWRITE_ROUNDS  # gap + rewriter rounds, never the reviewer
    assert "no claims" in result["output"]


def test_missing_facts_pause_for_the_user_and_resume_from_the_checkpoint():
    saver = InMemorySaver()
    _, graph, paused = _run(["Gap", NEEDS_INPUT_DRAFT], checkpointer=saver)

    assert "How many engineers did you mentor?" in paused["__interrupt__"][0].value["question"]
    assert "output" not in paused

    # A brand-new model and graph (as after a restart): only the checkpoint carries the earlier work over.
    model = Scripted(script=[GOOD_DRAFT, "APPROVED"], seen=[])
    resumed = ResumeWorkflow(RESUME, model, checkpointer=saver).build().invoke(
        Command(resume="Two"), {"configurable": {"thread_id": "t"}})

    assert model.calls == 2  # rewriter and reviewer; the gap analyst did not run again
    assert "Facts the user confirmed" in model.prompt(0) and "Two" in model.prompt(0)
    assert resumed["questions_asked"] == 1 and resumed["needs_user_input"] == []
    assert "approved" in resumed["output"]


def test_job_description_reaches_the_specialists_and_the_summary():
    state = {"job_description_text": "Requirements\n- Python, Docker and Kafka"}
    model, _, result = _run(["Gap: kafka", GOOD_DRAFT, "APPROVED"], state)

    assert result["job_description"]["required_skills"] == ["python", "docker", "kafka"]
    assert "Required skills: python, docker, kafka" in model.prompt(0)  # the gap analyst saw the structured job
    assert "Keywords the resume lacks (add only if the resume supports them): kafka" in model.prompt(1)
    assert "Job keywords still missing: kafka." in result["output"]


def test_without_a_job_description_the_workflow_still_runs():
    _, _, result = _run(["Gap", GOOD_DRAFT, "APPROVED"])

    assert result["job_description"] is None
    assert result["ats"]["against_job"] is False


@pytest.mark.parametrize("state, expected", [
    ({"needs_user_input": ["fact"], "questions_asked": 0}, "ask_user"),
    ({"needs_user_input": ["fact"], "questions_asked": MAX_QUESTION_ROUNDS}, "reviewer"),  # stop asking
    ({"needs_user_input": []}, "reviewer"),
    ({}, "reviewer"),
])
def test_route_after_rewrite(state, expected):
    assert ResumeWorkflow(RESUME, Scripted(script=[], seen=[])).after_rewrite(state) == expected


@pytest.mark.parametrize("state, expected", [
    ({"review": {"approved": True}, "rewrite_round": 1}, "finalize"),
    ({"review": {"approved": False}, "rewrite_round": 1}, "rewriter"),
    ({"review": {"approved": False}, "rewrite_round": MAX_REWRITE_ROUNDS}, "finalize"),
    ({"review": None, "rewrite_round": 1}, "rewriter"),
])
def test_route_after_review(state, expected):
    assert ResumeWorkflow(RESUME, Scripted(script=[], seen=[])).after_review(state) == expected


def test_graph_has_the_expected_nodes_and_edges():
    graph = ResumeWorkflow(RESUME, Scripted(script=[], seen=[])).build().get_graph()

    assert set(graph.nodes) == {"__start__", "analyze_job", "gap_analyst", "rewriter", "ask_user", "reviewer",
                                "finalize", "__end__"}
    assert {(e.source, e.target) for e in graph.edges} == {
        ("__start__", "analyze_job"), ("analyze_job", "gap_analyst"), ("gap_analyst", "rewriter"),
        ("rewriter", "ask_user"), ("rewriter", "reviewer"), ("ask_user", "rewriter"),
        ("reviewer", "rewriter"), ("reviewer", "finalize"), ("finalize", "__end__"),
    }
