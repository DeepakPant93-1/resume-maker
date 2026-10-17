"""The parsed resume, in the same shape (and snake_case names) as the Java service's `ResumeRequest`.

`metadata` is left out on purpose: the title and template are not in the resume text, and the ATS score is
computed by the Java service when it saves.
"""
from typing import Any

from pydantic import BaseModel, Field, model_validator


class LenientModel(BaseModel):
    """Accepts the usual slips of a small model instead of failing the whole parse.

    `null` where a list, flag or object is expected becomes its empty default, a list where text is expected is
    joined one item per line, and a number where text is expected becomes text. Wrong values are never invented.
    """

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        fixed = dict(data)
        for name, field in cls.model_fields.items():
            if name not in fixed:
                continue
            value = fixed[name]
            if value is None and not field.is_required() and field.default is None and field.default_factory is None:
                continue  # an optional text field: null is right
            if value is None:
                fixed[name] = field.get_default(call_default_factory=True)
            elif isinstance(value, list) and field.annotation == (str | None):
                fixed[name] = "\n".join(str(item) for item in value if item is not None)
            elif isinstance(value, (int, float)) and not isinstance(value, bool) and field.annotation == (str | None):
                fixed[name] = str(value)
        return fixed


class Profile(LenientModel):
    full_name: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    summary: str | None = None


class Experience(LenientModel):
    job_title: str | None = None
    company: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    current: bool = False
    achievements: str | None = None  # one line per bullet, each starting with "• "


class Education(LenientModel):
    degree: str | None = None
    university: str | None = None
    start_year: str | None = None
    end_year: str | None = None
    grade: str | None = None
    location: str | None = None


class Skills(LenientModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class Project(LenientModel):
    name: str | None = None
    description: str | None = None
    technologies: str | None = None  # one comma-separated string


class Certification(LenientModel):
    name: str | None = None
    issuer: str | None = None


class SpokenLanguage(LenientModel):
    language: str | None = None
    proficiency: str | None = None


class ParsedResume(LenientModel):
    profile: Profile = Field(default_factory=Profile)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    spoken_languages: list[SpokenLanguage] = Field(default_factory=list)
