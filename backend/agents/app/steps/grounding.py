"""Checks that a parsed resume only contains text that is really in the source text.

The model is told to copy, never rewrite. This is the deterministic backstop: any value that does not
appear in the source (ignoring whitespace, line breaks and bullet characters) is dropped, and logged.
"""
import logging
import re

from app.schemas.resume import ParsedResume

log = logging.getLogger(__name__)

_IGNORED = re.compile(r"[\s•●▪◦*·\-–—]+")


class TextGrounding:
    """Removes values from a `ParsedResume` that are not found in `source`."""

    def __init__(self, source: str) -> None:
        self._source = self._squash(source)
        self.dropped = 0

    @staticmethod
    def _squash(text: str) -> str:
        return _IGNORED.sub("", text)

    def _found(self, value: str) -> bool:
        return self._squash(value) in self._source

    def _scalar(self, owner: object, field: str) -> None:
        value = getattr(owner, field)
        if value is None:
            return
        if not value.strip():
            setattr(owner, field, None)
        elif not self._found(value):
            self._drop(field, value)
            setattr(owner, field, None)

    def _lines(self, owner: object, field: str) -> None:
        """A multi-line field (achievements): keep the lines that are in the source."""
        value = getattr(owner, field)
        if value is None:
            return
        kept = []
        for line in value.splitlines():
            if not self._squash(line):
                continue
            if self._found(line):
                kept.append(line)
            else:
                self._drop(field, line)
        setattr(owner, field, "\n".join(kept) or None)

    def _items(self, items: list[str], field: str) -> list[str]:
        kept = []
        for item in items:
            if self._found(item) and item.strip():
                kept.append(item)
            elif item.strip():
                self._drop(field, item)
        return kept

    def _drop(self, field: str, value: str) -> None:
        self.dropped += 1
        log.warning("Dropped %s: not found in the resume text (%d characters)", field, len(value))

    def apply(self, resume: ParsedResume) -> ParsedResume:
        """Cleans `resume` in place and returns it."""
        for field in ("full_name", "job_title", "email", "phone", "location", "linkedin", "summary"):
            self._scalar(resume.profile, field)
        for job in resume.experience:
            for field in ("job_title", "company", "start_date", "end_date"):
                self._scalar(job, field)
            self._lines(job, "achievements")
        for edu in resume.education:
            for field in ("degree", "university", "start_year", "end_year", "grade", "location"):
                self._scalar(edu, field)
        for group in ("languages", "frameworks", "tools"):
            setattr(resume.skills, group, self._items(getattr(resume.skills, group), f"skills.{group}"))
        for project in resume.projects:
            for field in ("name", "description", "technologies"):
                self._scalar(project, field)
        for cert in resume.certifications:
            for field in ("name", "issuer"):
                self._scalar(cert, field)
        for spoken in resume.spoken_languages:
            for field in ("language", "proficiency"):
                self._scalar(spoken, field)
        return resume
