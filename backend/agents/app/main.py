"""FastAPI entrypoint for the agent service."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import runs
from app.api.ats import router as ats_router
from app.api.runs import router as runs_router
from app.api.summary import router as summary_router
from app.core.config import get_settings
from app.core.llm import ModelFactory
from app.core.logging_config import setup_logging

setup_logging(get_settings().log_level)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Fails fast here if MongoDB is configured but unreachable. Runs cut off by the last shutdown can't
    # continue (their worker is gone), so mark them failed instead of leaving them "running" forever.
    persistence = runs.get_persistence()
    log.info("Agent service starting: %s, storage=%s", _models(settings),
             f"MongoDB ({settings.mongodb_database})" if settings.mongodb_uri else "in memory (lost on restart)")
    interrupted = persistence.runs.fail_interrupted()
    if interrupted:
        log.warning("Marked %d run(s) interrupted by the previous shutdown as failed", interrupted)
    yield
    log.info("Agent service stopped")


def _models(settings) -> str:
    """Provider, main model and fallback model, for the startup line."""
    try:
        factory = ModelFactory(settings)
        return (f"provider={settings.resolved_provider()}, model={factory.primary_name()}, "
                f"fallback={factory.fallback_name() or 'none'}")
    except ValueError:
        return "provider=NOT CONFIGURED (set GOOGLE_API_KEY or ANTHROPIC_API_KEY)"


app = FastAPI(title="Resume Maker Agent Service", lifespan=lifespan)
app.include_router(runs_router)
app.include_router(ats_router)
app.include_router(summary_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
