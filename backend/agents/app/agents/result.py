"""What a specialist agent hands back to the workflow."""
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpecialistResult:
    """A specialist's reply text plus structured fields to merge into the workflow state."""

    text: str
    update: dict[str, Any] = field(default_factory=dict)


# Specialist runner: takes the task text and the current workflow state, returns the specialist's
# reply (plain text, or a SpecialistResult that also updates the state).
SpecialistRunner = Callable[[str, Mapping[str, Any]], "str | SpecialistResult"]
