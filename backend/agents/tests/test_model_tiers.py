import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agents.specialists import SpecialistTeam
from app.core.config import Settings
from app.core.llm import ModelFactory


@pytest.fixture(autouse=True)
def _no_ambient_keys(monkeypatch):
    for key in ("ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "AGENTS_PROVIDER", "AGENTS_FALLBACK_MODEL",
                "AGENTS_ORCHESTRATOR_MODEL", "AGENTS_SUMMARY_MODEL", "AGENTS_REWRITE_MODEL"):
        monkeypatch.delenv(key, raising=False)


def _factory(**values) -> ModelFactory:
    return ModelFactory(Settings(_env_file=None, GOOGLE_API_KEY="g-key", **values))


def test_every_tier_uses_the_main_model_when_none_has_its_own_setting():
    factory = _factory(orchestrator_model="main-model")

    assert [factory.primary_name(t) for t in ("agent", "rewrite", "summary")] == ["main-model"] * 3
    assert factory.build_tier_models() == {}


def test_a_tier_with_its_own_setting_uses_it_and_the_others_keep_the_main_model():
    factory = _factory(orchestrator_model="main-model", summary_model="light-model", rewrite_model="mid-model")

    assert factory.primary_name("summary") == "light-model"
    assert factory.primary_name("rewrite") == "mid-model"
    assert factory.primary_name("agent") == "main-model"


def test_the_workflow_gets_a_rewrite_model_only_when_one_is_set():
    assert set(_factory(rewrite_model="mid-model").build_tier_models()) == {"rewrite"}
    assert _factory(summary_model="light-model").build_tier_models() == {}  # the summary is not a workflow task


def test_the_rewriter_uses_its_own_model_and_the_other_agents_the_main_one():
    main, rewrite = FakeListChatModel(responses=["MAIN"]), FakeListChatModel(responses=["REWRITE"])

    team = SpecialistTeam(main, {"id": "r1"}, tier_models={"rewrite": rewrite})

    assert team["rewriter"]("task", {}).text == "REWRITE"
    assert team["gap_analyst"]("task", {}).text == "MAIN"
