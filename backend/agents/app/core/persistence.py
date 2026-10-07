"""Where runs live: in memory, so everything is lost when the service restarts."""
import copy
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from langgraph.checkpoint.memory import InMemorySaver

RUNNING = "running"
WAITING_FOR_USER = "waiting_for_user"
COMPLETED = "completed"
FAILED = "failed"


class RunStore:
    """Keeps each run's record (status, question, output, error) and the workflow's graph checkpoints.

    The checkpointer holds the graph state (messages, claims, review...) so a run paused on `ask_user`
    can be resumed later. Methods are thread-safe because runs execute in background threads.
    """

    def __init__(self) -> None:
        self.checkpointer = InMemorySaver()
        self._runs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create(self, record: dict[str, Any]) -> None:
        with self._lock:
            self._runs[record["run_id"]] = {**copy.deepcopy(record), "created_at": self._now(), "updated_at": self._now()}

    def get(self, run_id: str) -> Optional[dict[str, Any]]:
        with self._lock:
            record = self._runs.get(run_id)
            return copy.deepcopy(record) if record else None

    def update(self, run_id: str, **fields: Any) -> None:
        with self._lock:
            self._runs[run_id].update(copy.deepcopy(fields), updated_at=self._now())

    def transition(self, run_id: str, expected_status: str, **fields: Any) -> bool:
        """Atomically apply `fields` only if the run is currently in `expected_status`."""
        with self._lock:
            record = self._runs.get(run_id)
            if record is None or record["status"] != expected_status:
                return False
            record.update(copy.deepcopy(fields), updated_at=self._now())
            return True

    def fail_interrupted(self) -> int:
        """Mark runs that were mid-flight when the service stopped as failed. Returns how many."""
        with self._lock:
            stuck = [record for record in self._runs.values() if record["status"] == RUNNING]
            for record in stuck:
                record.update(status=FAILED, error="Interrupted by a service restart", updated_at=self._now())
            return len(stuck)
