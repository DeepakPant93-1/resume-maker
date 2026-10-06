"""Job description extraction: raw text in, structured requirements out. Deterministic, no LLM."""
import re
from typing import Any, Optional

from app.steps.keywords import find_skills

JobDescription = dict[str, Any]

_REQUIRED_HEADING = re.compile(
    r"^(?:requirements?|qualifications?|must[- ]haves?|required(?: skills| qualifications)?|"
    r"what you(?:'|’)?ll need|what we(?:'|’)?re looking for|you have|skills)\b", re.IGNORECASE)
_PREFERRED_HEADING = re.compile(
    r"^(?:nice[- ]to[- ]haves?|preferred(?: skills| qualifications)?|bonus(?: points)?|good to have|"
    r"it(?:'|’)?s a plus|a plus)\b", re.IGNORECASE)
_OTHER_HEADING = re.compile(
    r"^(?:responsibilities|what you(?:'|’)?ll do|duties|about (?:us|the (?:role|team|company))|"
    r"benefits|perks|what we offer|why join us|overview|description|job description)\b", re.IGNORECASE)
_TITLE_LABEL = re.compile(r"^(?:job title|role|position|title)\s*[:\-]\s*(?P<title>.+)$", re.IGNORECASE)
_BULLET = re.compile(r"^\s*(?:[-•*●▪◦·]|\d+[.)])\s+")
_YEARS = re.compile(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


def _heading_kind(line: str) -> Optional[str]:
    """'required' / 'preferred' / 'other' for a short heading-like line, else None."""
    stripped = line.strip().rstrip(":").strip()
    if len(stripped) > 60 or _BULLET.match(line):
        return None
    for kind, pattern in (("required", _REQUIRED_HEADING), ("preferred", _PREFERRED_HEADING), ("other", _OTHER_HEADING)):
        if pattern.match(stripped) and len(stripped.split()) <= 6:
            return kind
    return None


def extract_jd(text: str) -> JobDescription:
    """Structure a pasted job description.

    Returns title, requirement and nice-to-have lines, the skills they mention (`required_skills`,
    `preferred_skills`, and `skills` for everything in the text) and the years of experience asked for.
    Without recognisable headings, every skill in the text counts as required.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    title: Optional[str] = None
    for line in lines:
        label = _TITLE_LABEL.match(line)
        if label:
            title = label.group("title").strip()
            break
    if title is None and lines and len(lines[0]) <= 80 and not lines[0].endswith(".") and not _heading_kind(lines[0]):
        title = lines[0]

    requirements: list[str] = []
    preferred: list[str] = []
    section: Optional[str] = None
    for line in lines:
        kind = _heading_kind(line)
        if kind:
            section = kind
            continue
        if section in ("required", "preferred"):
            (requirements if section == "required" else preferred).append(_BULLET.sub("", line).strip())

    skills = find_skills(text)
    if requirements or preferred:
        required_skills = find_skills("\n".join(requirements))
        preferred_skills = [s for s in find_skills("\n".join(preferred)) if s not in required_skills]
        # Skills named only in prose (summary, responsibilities) still count as required.
        mentioned = set(required_skills) | set(preferred_skills)
        required_skills += [s for s in skills if s not in mentioned]
    else:
        required_skills, preferred_skills = skills, []

    years = [int(m.group(1)) for m in _YEARS.finditer("\n".join(requirements) or text) if int(m.group(1)) <= 30]
    return {
        "title": title,
        "requirements": requirements,
        "preferred": preferred,
        "skills": skills,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "min_years": max(years) if years else None,
    }
