"""Deterministic handling of rewritten claims and their `source_ref`.

A claim is one rewritten resume statement plus a pointer into the original resume JSON
(`experience[0].achievements`). The rules here are code, not LLM judgement: a claim without a
resolvable `source_ref` is rejected no matter what the Reviewer model says.
"""
import re
from collections.abc import Mapping
from typing import Any, Optional

Claim = dict[str, Any]  # {"text": str, "source_ref": Optional[str], "section": Optional[str]}


class ClaimParser:
    """Splits a Rewriter draft into claims, and merges a new draft's claims into the earlier ones."""

    CLAIM_WITH_REF = re.compile(r"^\s*(?:[-•*]\s*)?(?P<text>.*?)\s*\[source_ref:\s*(?P<ref>.*?)\]\s*$", re.IGNORECASE)
    BULLET = re.compile(r"^\s*[-•*]\s+(?P<text>.+)$")
    NEEDS_INPUT_HEADING = re.compile(r"needs?\s+user\s+input", re.IGNORECASE)

    def parse(self, draft: str) -> tuple[list[Claim], list[str]]:
        """Split a Rewriter draft into claims and the "Needs user input" items.

        A line ending in `[source_ref: <path>]` is a claim. A bullet with no marker is still recorded as a
        claim (with `source_ref` None) so the Reviewer can reject it. Other lines are headings or prose.
        """
        claims: list[Claim] = []
        needs_input: list[str] = []
        section: Optional[str] = None
        in_needs_input = False
        for raw in draft.splitlines():
            line = raw.strip()
            if not line:
                continue
            if self.NEEDS_INPUT_HEADING.search(line) and not self.CLAIM_WITH_REF.match(line):
                in_needs_input = True
                continue
            with_ref = self.CLAIM_WITH_REF.match(line)
            bullet = self.BULLET.match(line)
            if in_needs_input:
                if bullet or with_ref:
                    needs_input.append((bullet.group("text") if bullet else line).strip())
                    continue
                in_needs_input = False  # a non-bullet line ends the list
            if with_ref:
                claims.append({"text": with_ref.group("text").strip(), "source_ref": with_ref.group("ref").strip() or None,
                               "section": section})
            elif bullet:
                claims.append({"text": bullet.group("text").strip(), "source_ref": None, "section": section})
            else:
                section = line.lstrip("#* ").rstrip(":* ").strip() or section
        return claims, needs_input

    def merge(self, existing: list[Claim], new: list[Claim]) -> list[Claim]:
        """Claims from a new draft replace earlier claims of the same section; other sections are kept."""
        replaced = {claim.get("section") for claim in new}
        return [claim for claim in existing if claim.get("section") not in replaced] + new


class ClaimValidator:
    """Checks claims against one original resume: every `source_ref` must point at something real in it."""

    REF_TOKEN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")

    def __init__(self, resume: Mapping[str, Any]) -> None:
        self.resume = resume

    def resolve(self, ref: str) -> Optional[Any]:
        """Return what `ref` points to in the resume, or None if the path is invalid, missing or empty."""
        ref = ref.strip()
        if not ref:
            return None
        node: Any = self.resume
        pos = 0
        while pos < len(ref):
            if ref[pos] == "." and pos > 0:
                pos += 1
            token = self.REF_TOKEN.match(ref, pos)
            if token is None:
                return None
            key, index = token.groups()
            if key is not None:
                if not isinstance(node, Mapping) or key not in node:
                    return None
                node = node[key]
            else:
                if not isinstance(node, list) or int(index) >= len(node):
                    return None
                node = node[int(index)]
            pos = token.end()
        return node if node not in (None, "", [], {}) else None

    def validate(self, claims: list[Claim]) -> list[str]:
        """Issues for claims whose `source_ref` is missing or does not exist in the original resume."""
        issues = []
        for number, claim in enumerate(claims, 1):
            ref = (claim.get("source_ref") or "").strip()
            label = f"Claim {number} ({claim['text'][:60]!r})"
            if not ref:
                issues.append(f"{label} has no source_ref")
            elif self.resolve(ref) is None:
                issues.append(f"{label} cites source_ref '{ref}', which does not exist in the original resume")
        return issues
