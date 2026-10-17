"""Summary Writer agent: writes or improves the professional summary from what the resume already says."""
from app.agents.base import SpecialistAgent

SUMMARY_WRITER_PROMPT = """\
You write the Professional Summary at the top of a resume.
Use only facts that appear in the resume below: job title, experience, skills, education. Never invent
employers, years of experience, metrics, tools or achievements. If the resume does not say it, leave it out.
Write 2-3 sentences, plain text, no heading, no bullets, no first-person pronouns ("I", "my").
If the task includes an existing summary, keep its meaning and facts, and make it tighter and clearer.
Reply with the summary text only: no preface, no quotes, no explanation.
"""


class SummaryWriterAgent(SpecialistAgent):
    """One model call that returns the summary text. It is not part of the tailoring workflow."""

    name = "summary_writer"
    tier = "summary"
    prompt = SUMMARY_WRITER_PROMPT

    def write(self, existing: str | None = None) -> str:
        """A new summary, or an improved version of `existing` when there is one."""
        existing = (existing or "").strip()
        task = ("Improve this professional summary:\n" + existing) if existing else "Write the professional summary."
        return str(self(task, {})).strip()
