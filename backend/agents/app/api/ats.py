"""ATS API: score a resume (optionally against a job description) right away. Plain code, no model call."""
import logging
from typing import Any

from pydantic import BaseModel, Field

from app.api.base import BaseRoutes
from app.steps.ats import AtsReport, AtsScorer
from app.steps.jd import JobDescriptionExtractor

log = logging.getLogger(__name__)


class AtsRequest(BaseModel):
    resume: dict[str, Any]
    job_description: str | None = Field(default=None, description="Pasted job posting; scores keyword match when given")


class AtsRoutes(BaseRoutes):
    """The endpoints under /api/ats."""

    prefix = "/api/ats"
    tag = "ats"

    def __init__(self) -> None:
        self.extractor = JobDescriptionExtractor()
        self.scorer = AtsScorer()
        super().__init__()

    def register(self) -> None:
        self.router.add_api_route("", self.score_resume, methods=["POST"])

    def score_resume(self, request: AtsRequest) -> AtsReport:
        text = (request.job_description or "").strip()
        report = self.scorer.score(request.resume, self.extractor.extract(text) if text else None)
        log.info("POST /api/ats: resume %s, job description: %s -> %s/100", request.resume.get("id"),
                 f"{len(text)} characters" if text else "none", report["score"])
        return report


router = AtsRoutes().router
