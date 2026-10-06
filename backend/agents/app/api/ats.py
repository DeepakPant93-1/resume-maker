"""ATS API: score a resume (optionally against a job description) right away. Plain code, no model call."""
import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.steps.ats import AtsReport, ats_score
from app.steps.jd import extract_jd

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ats", tags=["ats"])


class AtsRequest(BaseModel):
    resume: dict[str, Any]
    job_description: str | None = Field(default=None, description="Pasted job posting; scores keyword match when given")


@router.post("")
def score_resume(request: AtsRequest) -> AtsReport:
    text = (request.job_description or "").strip()
    report = ats_score(request.resume, extract_jd(text) if text else None)
    log.info("POST /api/ats: resume %s, job description: %s -> %s/100", request.resume.get("id"),
             f"{len(text)} characters" if text else "none", report["score"])
    return report
