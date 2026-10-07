"""Where runs and graph checkpoints live: in memory, so they are lost when the service restarts.

The checkpointer keeps the graph state (messages, claims, review...) so a run paused on `ask_user` can be
resumed later. The run store keeps each run's record (status, question, output, error).
"""
import copy
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from datetime import datetime, timezone
from typing import Any, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

RUNNING = "running"
WAITING_FOR_USER = "waiting_for_user"
COMPLETED = "completed"
FAILED = "failed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryRunStore:
    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, record: dict[str, Any]) -> None:
        with self._lock:
            self._runs[record["run_id"]] = {**copy.deepcopy(record), "created_at": _now(), "updated_at": _now()}

    def get(self, run_id: str) -> Optional[dict[str, Any]]:
        with self._lock:
            record = self._runs.get(run_id)
            return copy.deepcopy(record) if record else None

    def update(self, run_id: str, **fields: Any) -> None:
        with self._lock:
            self._runs[run_id].update(copy.deepcopy(fields), updated_at=_now())

    def transition(self, run_id: str, expected_status: str, **fields: Any) -> bool:
        """Atomically apply `fields` only if the run is currently in `expected_status`."""
        with self._lock:
            record = self._runs.get(run_id)
            if record is None or record["status"] != expected_status:
                return False
            record.update(copy.deepcopy(fields), updated_at=_now())
            return True

    def fail_interrupted(self) -> int:
        """Mark runs that were mid-flight when the service stopped as failed. Returns how many."""
        with self._lock:
            stuck = [r for r in self._runs.values() if r["status"] == RUNNING]
            for record in stuck:
                record.update(status=FAILED, error="Interrupted by a service restart", updated_at=_now())
            return len(stuck)


@dataclass
class Persistence:
    checkpointer: BaseCheckpointSaver = field(default_factory=InMemorySaver)
    runs: InMemoryRunStore = field(default_factory=InMemoryRunStore)


@lru_cache
def get_persistence() -> Persistence:
    """Process-wide persistence, created on first use."""
    return Persistence()
