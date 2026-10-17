"""Tailor to a job: start a real AI run on the saved resume, follow it, answer its questions, apply the result.

The work happens in the agent service; this page talks to it only through the Spring API (utils/api_client.py).
"""
import html as _html

import streamlit as st

from pages.my_resumes import initialize_resume_data
from styles.theme import card, css, donut, html, page_header
from utils.api_client import ApiError, answer_run, get_run, save_resume, start_run
from utils.run_helpers import apply_claims

_FOCUS_CSS = """
section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"] { display: none !important; }
"""


def _leave():
    st.session_state.page = st.session_state.get("agent_back", "MyResumes")
    st.session_state.agent_view = "workspace"
    st.session_state.pop("agent_back", None)
    st.rerun()


def _new_run():
    st.session_state.pop("run_id", None)
    st.rerun()


def _render_start():
    with card("runstart"):
        html('<div class="r-card-title">Job description</div>')
        job = st.text_area(
            "Job description", height=240, key="run_job", label_visibility="collapsed",
            placeholder="Paste the job posting here. Leave it empty for a general improvement of your resume.",
        )
        st.caption("Your resume is saved first, then the AI agents analyse the gaps, rewrite your summary and "
                   "experience, and fact-check every statement against your original resume.")
        if st.button("✦ Start AI run", type="primary", key="run_start"):
            try:
                with st.spinner("Saving your resume..."):
                    saved = save_resume(st.session_state.get("resume_id"), st.session_state.resume_data)
                    st.session_state.resume_id = saved["id"]
                    started = start_run(saved["id"], job)
            except ApiError as e:
                st.error(str(e))
                return
            st.session_state.run_id = started["run_id"]
            st.rerun()


@st.fragment(run_every="2s")
def _poll(run_id):
    """Re-check the run every two seconds; once it leaves 'running', rerun the page to show the new state."""
    try:
        still_running = get_run(run_id).get("status") == "running"
    except ApiError:
        still_running = False  # let the page itself show the error
    if not still_running:
        st.rerun()
    st.info("The AI agents are working on your resume. This usually takes about a minute.")


def _render_question(run):
    with card("runquestion"):
        html('<div class="r-card-title">The AI needs a few facts from you</div>')
        st.text(run.get("question") or "")
        with st.form("run_answer_form", clear_on_submit=True, border=False):
            answer = st.text_area("Your answer", height=120, placeholder="Answer here. Only share facts that are true.")
            sent = st.form_submit_button("Send answer →", type="primary")
        if sent:
            if not answer.strip():
                st.warning("Please type an answer first.")
                return
            try:
                answer_run(run["run_id"], answer)
            except ApiError as e:
                st.error(str(e))
                return
            st.rerun()


def _render_failed(run):
    with card("runfailed"):
        st.error("The AI run failed.")
        st.caption(run.get("error") or "No details were returned.")
        if st.button("Try again", type="primary", key="run_retry"):
            _new_run()


def _render_result(run):
    state = run.get("state") or {}
    claims = state.get("claims") or []
    review = state.get("review") or {}
    before, after = (state.get("ats") or {}).get("score"), (state.get("ats_with_draft") or {}).get("score")
    missing = (((state.get("ats_with_draft") or {}).get("components") or {}).get("keywords") or {}).get("missing")

    summary, details = st.columns([3, 2])
    with summary:
        with card("runsummary"):
            html('<div class="r-card-title">Result</div>')
            st.text(run.get("output") or "")
    with details:
        with card("runscore"):
            if after is not None:
                html('<div style="display:flex;gap:1rem;align-items:center">'
                     f'{donut(int(after), "#6C4FE0", 84)}'
                     f'<div><div class="r-label">ATS score</div>'
                     f'<div style="font-size:1.4rem;font-weight:700">{before} → {after}</div>'
                     '<div class="r-muted">with the new statements</div></div></div>')
            if missing:
                st.caption("Job keywords still missing: " + ", ".join(missing))
            if review.get("approved"):
                st.success("Fact-check passed: every statement traces back to your original resume.")
            elif review:
                st.warning("Some statements did not pass the fact-check:")
                for issue in review.get("issues") or []:
                    st.caption("• " + issue)

    with card("runclaims"):
        html('<div class="r-card-title">Rewritten statements</div>')
        if not claims:
            st.caption("No statements were produced.")
        for claim in claims:
            html(f'<div style="margin:0.5rem 0"><span class="r-badge soft">{_html.escape(claim.get("section") or "General")}</span>'
                 f'&nbsp; {_html.escape(claim["text"])}'
                 f'<div class="r-muted" style="margin-left:0.2rem">from your resume: {_html.escape(claim.get("source_ref") or "unknown")}</div></div>')
        if state.get("needs_user_input"):
            st.caption("Still needed from you: " + "; ".join(state["needs_user_input"]))

        apply_col, again_col, _ = st.columns([1.4, 1, 2])
        with apply_col:
            if st.button("Apply to my resume", type="primary", use_container_width=True, key="run_apply",
                         disabled=not claims):
                new_data, applied, skipped = apply_claims(st.session_state.resume_data, claims)
                st.session_state.resume_data = new_data
                st.session_state.pop("run_id", None)
                st.session_state.page = "MyResumes"
                st.session_state.agent_view = "workspace"
                note = f" ({skipped} could not be placed)" if skipped else ""
                st.toast(f"Applied {applied} statement(s) to your resume{note}. Review and Save.",
                         icon=":material/check_circle:")
                st.rerun()
        with again_col:
            if st.button("New run", use_container_width=True, key="run_again"):
                _new_run()
        st.caption("Applying replaces your summary and the bullets of each job that was rewritten. "
                   "Nothing is saved until you press Save in the editor.")


def render_run():
    initialize_resume_data()
    css(_FOCUS_CSS)
    with st.container(key="topbar"):
        html('<span style="font-weight:700;color:#6C4FE0;font-size:1.05rem">ResuAI</span>')
    if st.button("← Back", type="tertiary", key="run_back"):
        _leave()
    page_header("Tailor to a job", "Paste a job description and let the AI agents tailor your resume to it.")

    run_id = st.session_state.get("run_id")
    if not run_id:
        _render_start()
        return
    try:
        run = get_run(run_id)
    except ApiError as e:
        st.error(str(e))
        if st.button("Start over", key="run_reset"):
            _new_run()
        return

    status = run.get("status")
    if status == "running":
        _poll(run_id)
    elif status == "waiting_for_user":
        _render_question(run)
    elif status == "failed":
        _render_failed(run)
    else:
        _render_result(run)
