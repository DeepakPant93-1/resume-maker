"""Turns the Rewriter's draft text into claims. Plain code, no model call."""
import re
from typing import Any, Optional

# One rewritten resume statement, filed under the section heading it appeared below.
Claim = dict[str, Any]  # {"text": str, "section": Optional[str]}


class ClaimParser:
    """Reads a Rewriter draft into claims, and merges a new draft's claims into the earlier ones.

    A draft looks like this:

        Experience                      <- a heading line starts a section
        - Led migration to Kubernetes   <- each bullet is a claim in that section
        Needs user input                <- bullets below this are questions for the user, not claims
        - How many engineers did you mentor?
    """

    BULLET = re.compile(r"^\s*[-•*]\s+(?P<text>.+)$")
    NEEDS_INPUT_HEADING = re.compile(r"needs?\s+user\s+input", re.IGNORECASE)

    def parse(self, draft: str) -> tuple[list[Claim], list[str]]:
        """Return the claims in the draft and the "Needs user input" questions."""
        claims: list[Claim] = []
        questions: list[str] = []
        section: Optional[str] = None
        in_questions = False

        for line in (raw.strip() for raw in draft.splitlines()):
            if not line:
                continue
            bullet = self.BULLET.match(line)
            if bullet and in_questions:
                questions.append(bullet.group("text").strip())
            elif bullet:
                claims.append({"text": bullet.group("text").strip(), "section": section})
            elif self.NEEDS_INPUT_HEADING.search(line):
                in_questions = True
            else:  # any other line is a section heading, and it ends the questions list
                in_questions = False
                section = line.lstrip("#* ").rstrip(":* ").strip() or section
        return claims, questions

    def merge(self, existing: list[Claim], new: list[Claim]) -> list[Claim]:
        """Claims from a new draft replace earlier claims of the same section; other sections are kept."""
        replaced_sections = {claim["section"] for claim in new}
        kept = [claim for claim in existing if claim["section"] not in replaced_sections]
        return kept + new
