"""Console logging for the agent service, in the same shape as the Spring service's log lines.

uvicorn only configures its own loggers, so without this the service's own `log.info(...)` calls print nothing
(the root logger defaults to WARNING). The level comes from `AGENTS_LOG_LEVEL` (default INFO).

Every line carries the id of the run it belongs to (first 8 characters, "-" outside a run): set it with
`run_context(run_id)` and any logger called within, including graph nodes on worker threads, picks it up.
"""
import logging
from contextlib import contextmanager
from contextvars import ContextVar

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-5s [%(threadName)s] [run %(run)s] %(name)s - %(message)s"
DATE_FORMAT = "%H:%M:%S"

# Chatty third-party loggers stay at WARNING even when the service runs at DEBUG.
_QUIET = ("httpx", "httpcore", "urllib3", "google_genai", "anthropic", "langchain_google_genai")

_run_id: ContextVar[str] = ContextVar("run_id", default="-")


class RunFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.run = _run_id.get()[:8]
        return True


@contextmanager
def run_context(run_id: str):
    """Tag every log line written inside this block with `run_id`."""
    token = _run_id.set(run_id)
    try:
        yield
    finally:
        _run_id.reset(token)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format=LOG_FORMAT, datefmt=DATE_FORMAT, force=True)
    for handler in logging.getLogger().handlers:
        handler.addFilter(RunFilter())
    for name in _QUIET:
        logging.getLogger(name).setLevel(logging.WARNING)
