"""Parse API: turns the raw text of an uploaded resume into the structured resume."""
import logging

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.agents.resume_parser import ResumeParseError, ResumeParserAgent
from app.api.base import BaseRoutes
from app.core.llm import ModelFactory
from app.schemas.resume import ParsedResume

log = logging.getLogger(__name__)


class ParseRequest(BaseModel):
    text: str = Field(description="The text extracted from the uploaded resume")


class ParseRoutes(BaseRoutes):
    """The endpoint under /api/parse."""

    prefix = "/api/parse"
    tag = "parse"

    def register(self) -> None:
        self.router.add_api_route("", self.parse_resume, methods=["POST"], response_model=ParsedResume)

    def parse_resume(self, request: ParseRequest) -> ParsedResume:
        if not request.text.strip():
            raise HTTPException(status_code=422, detail="The resume text is empty")
        log.info("POST /api/parse: %d characters", len(request.text))
        try:
            models = ModelFactory()
            return ResumeParserAgent(
                models.build_primary(ResumeParserAgent.tier), models.build_fallback()
            ).parse(request.text)
        except ValueError as exc:  # no provider / API key configured
            log.error("Resume not parsed: %s", exc)
            raise HTTPException(status_code=503, detail="The AI model is not configured") from exc
        except ResumeParseError as exc:
            log.error("Resume not parsed: %s", exc)
            raise HTTPException(status_code=502, detail="The AI model did not return a usable resume") from exc


router = ParseRoutes().router
