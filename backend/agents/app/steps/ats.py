"""ATS score: how well applicant tracking systems can read the resume and match it to a job. Deterministic.

Points (out of 100) with a job description: keyword match 50, completeness 25, measurable impact 15,
readability 10. Without one the keyword part is dropped and the rest are scaled up to 100. This is a
transparent heuristic for guidance, not any specific vendor's ATS algorithm.
"""
import re
from collections.abc import Mapping
from typing import Any, Optional

from app.steps.jd import JobDescription
from app.steps.keywords import KeywordMatcher

AtsReport = dict[str, Any]


class AtsScorer:
    """Scores a resume for ATS readability and keyword match. Holds the keyword matcher it scores with."""

    BULLET_PREFIX = re.compile(r"^\s*[-•*●▪◦·]\s*")
    HAS_NUMBER = re.compile(r"\d")
    MAX_SUMMARY_WORDS = 120
    MAX_BULLET_WORDS = 35

    def __init__(self, matcher: Optional[KeywordMatcher] = None) -> None:
        self.matcher = matcher or KeywordMatcher()

    @staticmethod
    def _text(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @staticmethod
    def _scaled(max_points: float, fraction: float) -> float:
        return round(max_points * fraction, 1)

    @classmethod
    def resume_bullets(cls, resume: Mapping[str, Any]) -> list[str]:
        """Every achievement bullet across the experience entries."""
        bullets = []
        for job in resume.get("experience") or []:
            for line in cls._text(job.get("achievements")).splitlines():
                line = cls.BULLET_PREFIX.sub("", line).strip()
                if line:
                    bullets.append(line)
        return bullets

    @classmethod
    def resume_text(cls, resume: Mapping[str, Any]) -> str:
        """All resume content flattened to one string, for keyword matching."""
        text = cls._text
        profile = resume.get("profile") or {}
        skills = resume.get("skills") or {}
        parts = [text(profile.get("job_title")), text(profile.get("summary"))]
        for group in ("languages", "frameworks", "tools"):
            parts.extend(s for s in skills.get(group) or [] if isinstance(s, str))
        for job in resume.get("experience") or []:
            parts += [text(job.get("job_title")), text(job.get("company")), text(job.get("achievements"))]
        for project in resume.get("projects") or []:
            parts += [text(project.get("name")), text(project.get("description")), text(project.get("technologies"))]
        for cert in resume.get("certifications") or []:
            parts.append(text(cert.get("name")))
        return "\n".join(p for p in parts if p)

    def score(self, resume: Mapping[str, Any], jd: Optional[JobDescription] = None, extra_text: str = "") -> AtsReport:
        """Score `resume` (optionally against `jd`). `extra_text` (e.g. rewritten claims) counts for keyword matching."""
        text, scaled = self._text, self._scaled
        use_keywords = bool(jd and (jd.get("required_skills") or jd.get("preferred_skills")))
        weights = {"keywords": 50, "completeness": 25, "impact": 15, "readability": 10} if use_keywords else \
                  {"keywords": 0, "completeness": 50, "impact": 30, "readability": 20}
        components: dict[str, dict[str, Any]] = {}
        suggestions: list[str] = []

        # Keyword match: required skills weigh 1, nice-to-haves 0.5.
        if use_keywords:
            have = set(self.matcher.find(self.resume_text(resume) + "\n" + extra_text))
            required, preferred = jd.get("required_skills") or [], jd.get("preferred_skills") or []
            total = len(required) + 0.5 * len(preferred)
            got = sum(1 for s in required if s in have) + 0.5 * sum(1 for s in preferred if s in have)
            missing = [s for s in required + preferred if s not in have]
            components["keywords"] = {
                "points": scaled(weights["keywords"], got / total), "max": weights["keywords"],
                "matched": [s for s in required + preferred if s in have], "missing": missing,
            }
            if missing:
                suggestions.append("Job keywords missing from the resume: " + ", ".join(missing)
                                   + ". Only add the ones you can truthfully support.")

        # Completeness: the basics every ATS parser looks for.
        profile = resume.get("profile") or {}
        skills = resume.get("skills") or {}
        checks = {
            "name": bool(text(profile.get("full_name"))),
            "email": bool(text(profile.get("email"))),
            "phone": bool(text(profile.get("phone"))),
            "summary": bool(text(profile.get("summary"))),
            "experience": bool(resume.get("experience")),
            "education": bool(resume.get("education")),
            "skills": any(skills.get(g) for g in ("languages", "frameworks", "tools")),
        }
        missing_parts = [name for name, ok in checks.items() if not ok]
        components["completeness"] = {
            "points": scaled(weights["completeness"], 1 - len(missing_parts) / len(checks)),
            "max": weights["completeness"], "missing": missing_parts,
        }
        if missing_parts:
            suggestions.append("Add the missing section(s): " + ", ".join(missing_parts) + ".")

        # Impact: bullets that carry a number (%, counts, money, time) read as measurable results.
        bullets = self.resume_bullets(resume)
        with_numbers = sum(1 for b in bullets if self.HAS_NUMBER.search(b))
        components["impact"] = {
            "points": scaled(weights["impact"], with_numbers / len(bullets)) if bullets else 0.0,
            "max": weights["impact"], "bullets": len(bullets), "with_numbers": with_numbers,
        }
        if not bullets:
            suggestions.append("Add achievement bullets under each job.")
        elif with_numbers < len(bullets):
            suggestions.append(f"Only {with_numbers} of {len(bullets)} bullets show measurable impact; add numbers.")

        # Readability: a tight summary and short bullets parse and skim well.
        summary_words = len(text(profile.get("summary")).split())
        long_bullets = [b for b in bullets if len(b.split()) > self.MAX_BULLET_WORDS]
        readability_checks = [summary_words <= self.MAX_SUMMARY_WORDS, not long_bullets]
        components["readability"] = {
            "points": scaled(weights["readability"], sum(readability_checks) / len(readability_checks)),
            "max": weights["readability"], "long_bullets": len(long_bullets), "summary_words": summary_words,
        }
        if summary_words > self.MAX_SUMMARY_WORDS:
            suggestions.append(f"Shorten the summary to under {self.MAX_SUMMARY_WORDS} words (now {summary_words}).")
        if long_bullets:
            suggestions.append(f"{len(long_bullets)} bullet(s) run over {self.MAX_BULLET_WORDS} words; split or trim them.")

        components = {name: part for name, part in components.items() if part["max"]}
        return {
            "score": round(sum(part["points"] for part in components.values())),
            "against_job": use_keywords,
            "components": components,
            "suggestions": suggestions,
        }
