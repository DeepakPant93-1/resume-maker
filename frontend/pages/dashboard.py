"""
Dashboard page - matches the Figma "Good evening, Suraj" screen
"""
import html as _html
import re
from datetime import datetime, timezone

import streamlit as st
from styles.theme import html, page_header, stat_card
from utils.api_client import ApiError, delete_resume, get_resume, list_applications, list_resumes, to_editor_data
from utils.resume_export import (DOCX_MIME, MARKDOWN_MIME, PDF_MIME, file_stem, to_docx, to_markdown,
                                 to_pdf)

_CSS = """
<style>
.st-key-hero {
    background: #EFEBFD; border-radius: 12px;
    padding: 1.25rem 1.5rem; margin-bottom: 0.75rem;
}
.r-resume-card {
    background: #FFFFFF; border: 1px solid #E6E8EF; border-radius: 12px;
    padding: 1rem; margin-bottom: 1rem;
}
.r-resume-thumb {
    background: #F5F6FA; border-radius: 8px; height: 110px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 0.9rem;
}
.r-resume-name { font-size: 0.95rem; font-weight: 600; color: #111827; }
.r-resume-meta { font-size: 0.75rem; color: #6B7280; margin: 0.15rem 0 0.6rem; }
.r-section-title { font-size: 1.05rem; font-weight: 600; color: #111827; margin: 1.25rem 0 0.75rem; }
.st-key-hero button p { white-space: nowrap; font-size: 0.8rem !important; }
</style>
"""

_DOC_ICON = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6C4FE0" '
    'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
    '<path d="M14 3v5h5"/><path d="M9 13h6"/><path d="M9 17h6"/></svg>'
)


def _greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def _go(page_key):
    st.session_state.page = page_key
    st.rerun()


def _ago(updated_at):
    """'5 min ago' style text for an ISO timestamp from the backend; resumes saved before timestamps existed have none."""
    if not updated_at:
        return "Saved earlier"
    try:
        # Python 3.9 cannot parse a trailing Z or varying fraction digits, and the fraction is not needed here.
        saved = datetime.fromisoformat(re.sub(r"\.\d+", "", updated_at).replace("Z", "+00:00"))
    except ValueError:
        return "Saved earlier"
    seconds = (datetime.now(timezone.utc) - saved).total_seconds()
    if seconds < 60:
        return "Updated just now"
    if seconds < 3600:
        return f"Updated {int(seconds // 60)} min ago"
    if seconds < 86400:
        return f"Updated {int(seconds // 3600)} h ago"
    if seconds < 7 * 86400:
        return f"Updated {int(seconds // 86400)} d ago"
    return "Updated " + saved.astimezone().strftime("%d %b %Y")


def _load_resumes():
    """(resumes, error): the saved resumes from the backend, or an empty list and a message if it is unreachable."""
    try:
        return list_resumes(), None
    except ApiError as e:
        return [], str(e)


def _open_resume(resume_id):
    """Load a saved resume into the editor and go there."""
    try:
        resume = get_resume(resume_id)
    except ApiError as e:
        st.error(str(e))
        return
    st.session_state.resume_data = to_editor_data(resume)
    st.session_state.resume_id = resume["id"]
    _go("MyResumes")


@st.dialog("Download resume")
def _download_dialog(resume_id, title):
    """Fetch the saved resume and offer it as a PDF, Word document or Markdown file."""
    try:
        data = to_editor_data(get_resume(resume_id))
    except ApiError as e:
        st.error(str(e))
        return
    st.caption(title)
    stem = file_stem(data)
    st.download_button("Download as PDF (.pdf)", to_pdf(data), f"{stem}.pdf", PDF_MIME,
                       type="primary", use_container_width=True, key=f"dl_pdf_{resume_id}")
    st.download_button("Download as Word (.docx)", to_docx(data), f"{stem}.docx", DOCX_MIME,
                       use_container_width=True, key=f"dl_docx_{resume_id}")
    st.download_button("Download as Markdown (.md)", to_markdown(data), f"{stem}.md", MARKDOWN_MIME,
                       use_container_width=True, key=f"dl_md_{resume_id}")


@st.dialog("Delete resume")
def _delete_dialog(resume_id, title):
    """Ask for confirmation, then delete the saved resume."""
    st.write(f"Delete **{title}**? This cannot be undone.")
    yes, no = st.columns(2)
    with no:
        if st.button("Cancel", use_container_width=True, key=f"del_no_{resume_id}"):
            st.rerun()
    with yes:
        if st.button("Delete", type="primary", use_container_width=True, key=f"del_yes_{resume_id}"):
            try:
                delete_resume(resume_id)
            except ApiError as e:
                if e.status_code != 404:  # already gone is fine: the list below refreshes either way
                    st.error(str(e))
                    return
            if st.session_state.get("resume_id") == resume_id:
                # The editor still holds it: forget it, so Save creates a new resume instead of updating a deleted one.
                st.session_state.resume_id = None
                st.session_state.pop("resume_data", None)
            st.toast("Resume deleted", icon=":material/check_circle:")
            st.rerun()


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    first_name = st.session_state.get("user", {}).get("name", "there").split()[0]
    page_header(f"{_greeting()}, {first_name} 👋", "Build, optimize and land your next opportunity with AI.")

    # ---- Hero banner ----
    with st.container(key="hero"):
        text, b1, b2 = st.columns([5, 3, 2], vertical_alignment="center")
        with text:
            html(
                '<p class="r-hero-title">Create your resume with AI</p>'
                '<p class="r-hero-sub">Generate an ATS-friendly resume in minutes.</p>'
            )
        with b1:
            if st.button("\\+ Create New Resume", type="primary", use_container_width=True, key="hero_create"):
                _go("CreateResume")
        with b2:
            if st.button("Choose Template", use_container_width=True, key="hero_template"):
                _go("Templates")

    # ---- Stats ----
    resumes, load_error = _load_resumes()
    try:
        applications_count = len(list_applications())
    except ApiError:
        applications_count = "—"
    scores = [r["ats_score"] for r in resumes if r.get("ats_score") is not None]
    stats = [
        ("Total Resumes", len(resumes), None),
        ("Applications", applications_count, None),
        ("Best ATS Score", f"{max(scores)}%" if scores else "—", "#22A06B"),
        ("AI Credits", st.session_state.get("ai_credits", 50), "#6C4FE0"),  # no backend for this yet
    ]
    for col, (label, value, color) in zip(st.columns(4), stats):
        with col:
            stat_card(label, value, color)

    # ---- Your Resumes ----
    html('<div class="r-section-title">Your Resumes</div>')
    if load_error:
        st.warning(f"Could not load your resumes: {load_error}")
        return
    if not resumes:
        html('<div class="r-card r-muted">No resumes yet. Create your first one above.</div>')
        return

    cols = st.columns(3)
    for i, r in enumerate(resumes):
        with cols[i % 3]:
            score = r.get("ats_score")
            badge = (f'<span class="r-badge">✓ ATS {score}%</span>' if score is not None
                     else '<span class="r-badge idle">ATS —</span>')
            html(
                f'<div class="r-resume-card">'
                f'<div class="r-resume-thumb">{_DOC_ICON}</div>'
                f'<div class="r-resume-name">{_html.escape(r["title"])}</div>'
                f'<div class="r-resume-meta">{_ago(r.get("updated_at"))}</div>'
                f'{badge}'
                f'</div>'
            )
            if st.button("Open in editor", key=f"open_{r['id']}", use_container_width=True):
                _open_resume(r["id"])
            download, delete = st.columns(2)
            with download:
                if st.button("Download", key=f"download_{r['id']}", use_container_width=True):
                    _download_dialog(r["id"], r["title"])
            with delete:
                if st.button("Delete", key=f"delete_{r['id']}", use_container_width=True):
                    _delete_dialog(r["id"], r["title"])
