from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from app.agents.orchestrator import SPECIALISTS
from app.agents.specialists import PROMPTS, build_specialists


class RecordingModel(GenericFakeChatModel):
    seen: list = []

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.seen.append(messages)
        return super()._generate(messages, stop, run_manager, **kwargs)


def test_prompts_cover_every_orchestrator_specialist():
    assert PROMPTS.keys() == SPECIALISTS.keys()


def test_runner_binds_resume_and_returns_reply_text():
    model = RecordingModel(messages=iter([AIMessage(content="APPROVED")]), seen=[])
    runners = build_specialists(model, {"id": "r1", "profile": {"name": "Arjun"}})

    assert runners["reviewer"]("check the draft", {}).text == "APPROVED"

    system, human = model.seen[0]
    assert "Arjun" in system.content and "REJECTED" in system.content
    assert human.content == "check the draft"
