from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from app.agents.base import SpecialistAgent
from app.agents.specialists import PROMPTS, SpecialistTeam
from app.steps.ats import AtsScorer
from app.steps.jd import JobDescriptionExtractor


class RecordingModel(GenericFakeChatModel):
    seen: list = []

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.seen.append(messages)
        return super()._generate(messages, stop, run_manager, **kwargs)


RESUME = {
    "profile": {"full_name": "A", "email": "a@x.io", "phone": "1", "summary": "Python dev"},
    "experience": [{"achievements": "• Cut costs 30% with Docker"}],
    "education": [{"degree": "B.Tech"}],
    "skills": {"languages": ["Python"], "frameworks": [], "tools": ["Docker"]},
}
JD_TEXT = "Requirements\n- Python, Docker and Kafka"


def test_prompts_cover_every_specialist():
    assert PROMPTS.keys() == {"gap_analyst", "rewriter", "reviewer"}


def test_specialists_receive_the_structured_job_and_missing_keywords():
    jd = JobDescriptionExtractor().extract(JD_TEXT)
    block = SpecialistAgent._job_block({"job_description": jd, "ats": AtsScorer().score(RESUME, jd)})

    assert "Required skills: python, docker, kafka" in block
    assert "Keywords the resume lacks (add only if the resume supports them): kafka" in block
    assert SpecialistAgent._job_block({}) == ""


def test_runner_binds_resume_and_returns_reply_text():
    model = RecordingModel(messages=iter([AIMessage(content="APPROVED")]), seen=[])
    runners = SpecialistTeam(model, {"id": "r1", "profile": {"name": "Arjun"}})

    assert runners["reviewer"]("check the draft", {}).text == "APPROVED"

    system, human = model.seen[0]
    assert "Arjun" in system.content and "REJECTED" in system.content
    assert human.content == "check the draft"
