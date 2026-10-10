"""Summary API: write or improve the professional summary for the resume editor's "Write with AI" button."""
import logging
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.agents.summary import SummaryWriterAgent
from app.api.base import BaseRoutes
from app.core.llm import ModelFactory

log = logging.getLogger(__name__)


class SummaryRequest(BaseModel):
    resume: dict[str, Any] = Field(description="The resume as the editor has it (profile, experience, skills...)")
    summary: str | None = Field(default=None, description="The summary typed so far; improved when given")


class SummaryResponse(BaseModel):
    summary: str


class SummaryRoutes(BaseRoutes):
    """The endpoint under /api/summary."""

    prefix = "/api/summary"
    tag = "summary"

    def register(self) -> None:
        self.router.add_api_route("", self.write_summary, methods=["POST"])

    @staticmethod
    def _has_material(resume: dict[str, Any], existing: str) -> bool:
        """True when there is something real to write from: a job title, an experience entry, skills or a summary."""
        profile = resume.get("profile") or {}
        skills = resume.get("skills") or {}
        return bool(
            existing
            or (profile.get("job_title") or "").strip()
            or any((job.get("job_title") or job.get("achievements") or "").strip() for job in resume.get("experience") or [])
            or any(skills.get(group) for group in ("languages", "frameworks", "tools"))
        )

    def write_summary(self, request: SummaryRequest) -> SummaryResponse:
        existing = (request.summary or "").strip()
        if not self._has_material(request.resume, existing):
            raise HTTPException(
                status_code=422,
                detail="Add your job title, some experience or skills first, so the summary has facts to use",
            )
        log.info("POST /api/summary: %s", "improving the existing summary" if existing else "writing a new summary")
        try:
            models = ModelFactory()
            text = SummaryWriterAgent(
                models.build_primary(SummaryWriterAgent.tier), request.resume, models.build_fallback()
            ).write(existing)
        except ValueError as exc:  # no provider / API key configured
            log.error("Summary not written: %s", exc)
            raise HTTPException(status_code=503, detail="The AI model is not configured") from exc
        if not text:
            raise HTTPException(status_code=502, detail="The AI model returned an empty summary")
        return SummaryResponse(summary=text)


router = SummaryRoutes().router
