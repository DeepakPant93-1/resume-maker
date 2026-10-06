"""Deterministic steps exposed to the Orchestrator as tools (no model call inside).

Both tools write their result into the shared run state, so the specialists and the API read it from there.
"""
from typing import Any

from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.types import Command

from app.steps.ats import AtsReport, ats_score
from app.steps.claims import Claim
from app.steps.jd import JobDescription, extract_jd


def format_jd(jd: JobDescription) -> str:
    parts = [f"Title: {jd.get('title') or 'unknown'}"]
    if jd.get("min_years"):
        parts.append(f"Experience asked for: {jd['min_years']}+ years")
    parts.append(f"Requirements found: {len(jd.get('requirements') or [])}")
    parts.append("Required skills: " + (", ".join(jd.get("required_skills") or []) or "none recognised"))
    if jd.get("preferred_skills"):
        parts.append("Preferred skills: " + ", ".join(jd["preferred_skills"]))
    return "\n".join(parts)


def format_ats(report: AtsReport) -> str:
    kind = "against the job description" if report["against_job"] else "general readability (no job description)"
    lines = [f"ATS score: {report['score']}/100 ({kind})"]
    for name, part in report["components"].items():
        lines.append(f"- {name}: {part['points']}/{part['max']}")
    lines += [f"Suggestion: {s}" for s in report["suggestions"]]
    return "\n".join(lines)


def build_step_tools(resume: dict[str, Any]) -> list[BaseTool]:
    """Tools bound to one run's original resume."""

    @tool("extract_jd")
    def extract_jd_tool(text: str, runtime: ToolRuntime) -> Command:
        """Structure a pasted job description (title, requirements, required and preferred skills, years)
        and save it to the run. Also re-scores the resume against it."""
        jd = extract_jd(text)
        report = ats_score(resume, jd)
        message = format_jd(jd) + "\n\n" + format_ats(report)
        return Command(update={
            "job_description": jd,
            "ats": report,
            "messages": [ToolMessage(message, tool_call_id=runtime.tool_call_id)],
        })

    @tool("ats_score")
    def ats_score_tool(runtime: ToolRuntime, include_draft: bool = False) -> Command:
        """Score the original resume for ATS readability and keyword match against the saved job description.
        With include_draft=true, the rewritten claims count towards keyword matching, to preview the effect."""
        claims: list[Claim] = (runtime.state.get("claims") or []) if include_draft else []
        report = ats_score(resume, runtime.state.get("job_description"), "\n".join(c["text"] for c in claims))
        return Command(update={
            "ats": report,
            "messages": [ToolMessage(format_ats(report), tool_call_id=runtime.tool_call_id)],
        })

    return [extract_jd_tool, ats_score_tool]
