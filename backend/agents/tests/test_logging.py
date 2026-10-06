import io
import logging

import pytest

from app.core.logging_config import DATE_FORMAT, LOG_FORMAT, RunFilter, run_context
from app.graph.workflow import ResumeWorkflow
from tests.test_workflow import GOOD_DRAFT, RESUME, Scripted


@pytest.fixture
def log_output():
    """Capture the service's log lines formatted exactly as in production, including the run id."""
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    handler.addFilter(RunFilter())
    root = logging.getLogger()
    previous_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    yield buffer
    root.removeHandler(handler)
    root.setLevel(previous_level)


def test_a_run_logs_each_step_in_order_tagged_with_its_run_id(log_output):
    model = Scripted(script=["Gap: kafka", GOOD_DRAFT, "APPROVED"], seen=[])
    graph = ResumeWorkflow(RESUME, model).build()

    with run_context("abcdef1234567890"):
        graph.invoke({"job_description_text": "Requirements\n- Python and Kafka"})

    lines = log_output.getvalue().splitlines()
    assert lines and all("[run abcdef12]" in line for line in lines)  # even from the graph's worker threads
    steps = [next(w for w in ("analyze_job", "gap_analyst: model", "rewriter: drafting", "rewriter: 2 claim",
                              "reviewer: approved", "finalize") if w in line)
             for line in lines if any(w in line for w in ("analyze_job", "gap_analyst: model", "rewriter: drafting",
                                                           "rewriter: 2 claim", "reviewer: approved", "finalize"))]
    assert steps == ["analyze_job", "gap_analyst: model", "rewriter: drafting", "rewriter: 2 claim",
                     "reviewer: approved", "finalize"]


def test_logs_describe_the_work_without_leaking_resume_or_job_text(log_output):
    model = Scripted(script=["Gap: kafka", GOOD_DRAFT, "APPROVED"], seen=[])

    with run_context("r1"):
        ResumeWorkflow(RESUME, model).build().invoke({"job_description_text": "Requirements\n- Python and Kafka"})

    text = log_output.getvalue()
    assert "ATS baseline" in text and "model replied in" in text
    for private in ("Backend engineer", "a@x.io", "Kafka", "Acme"):  # resume summary, email, JD text, employer
        assert private not in text.replace("kafka", "")  # skill names are lower-cased counts at most, never text


def test_lines_outside_a_run_show_a_dash(log_output):
    logging.getLogger("app.test").info("hello")

    assert "[run -]" in log_output.getvalue()
