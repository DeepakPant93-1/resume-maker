"""Where runs and graph checkpoints live: MongoDB when AGENTS_MONGODB_URI is set, otherwise in memory.

The checkpointer keeps the graph state (messages, claims, review...) so a run paused on `ask_user` can be
resumed even after a restart. The run store keeps each run's record (status, question, output, error).
"""
import copy
import threading
from dataclasses import dataclass
from functools import lru_cache
from datetime import datetime, timezone
from typing import Any, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import Settings, get_settings

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


class MongoRunStore:
    def __init__(self, collection: Any) -> None:
        self._runs = collection

    def create(self, record: dict[str, Any]) -> None:
        self._runs.insert_one({"_id": record["run_id"], **record, "created_at": _now(), "updated_at": _now()})

    def get(self, run_id: str) -> Optional[dict[str, Any]]:
        record = self._runs.find_one({"_id": run_id})
        if record:
            record.pop("_id")
        return record

    def update(self, run_id: str, **fields: Any) -> None:
        self._runs.update_one({"_id": run_id}, {"$set": {**fields, "updated_at": _now()}})

    def transition(self, run_id: str, expected_status: str, **fields: Any) -> bool:
        result = self._runs.update_one(
            {"_id": run_id, "status": expected_status}, {"$set": {**fields, "updated_at": _now()}}
        )
        return result.modified_count == 1

    def fail_interrupted(self) -> int:
        result = self._runs.update_many(
            {"status": RUNNING},
            {"$set": {"status": FAILED, "error": "Interrupted by a service restart", "updated_at": _now()}},
        )
        return result.modified_count


@dataclass
class Persistence:
    checkpointer: BaseCheckpointSaver
    runs: InMemoryRunStore | MongoRunStore


def build_persistence(settings: Settings) -> Persistence:
    if not settings.mongodb_uri:
        return Persistence(InMemorySaver(), InMemoryRunStore())

    from langgraph.checkpoint.mongodb import MongoDBSaver
    from pymongo import MongoClient

    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # fail at startup, not on the first run
    database = client[settings.mongodb_database]
    checkpointer = MongoDBSaver(
        client,
        db_name=settings.mongodb_database,
        checkpoint_collection_name="agent_checkpoints",
        writes_collection_name="agent_checkpoint_writes",
    )
    return Persistence(checkpointer, MongoRunStore(database["agent_runs"]))


@lru_cache
def get_persistence() -> Persistence:
    """Process-wide persistence, built on first use from the environment settings."""
    return build_persistence(get_settings())
