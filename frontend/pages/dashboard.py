"""
Dashboard page - matches the Figma "Good evening, Suraj" screen
"""
from datetime import datetime

import streamlit as st
from styles.theme import html, page_header, stat_card

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
    resumes = st.session_state.get("resumes", [])
    best_ats = max((r.get("ats_score", 0) for r in resumes), default=0)
    stats = [
        ("Total Resumes", len(resumes), None),
        ("Applications", st.session_state.get("applications_count", 12), None),
        ("Best ATS Score", f"{best_ats}%", "#22A06B"),
        ("AI Credits", st.session_state.get("ai_credits", 50), "#6C4FE0"),
    ]
    for col, (label, value, color) in zip(st.columns(4), stats):
        with col:
            stat_card(label, value, color)

    # ---- Your Resumes ----
    html('<div class="r-section-title">Your Resumes</div>')
    if not resumes:
        html('<div class="r-card r-muted">No resumes yet. Create your first one above.</div>')
        return

    cols = st.columns(3)
    for i, r in enumerate(resumes):
        with cols[i % 3]:
            html(
                f'<div class="r-resume-card">'
                f'<div class="r-resume-thumb">{_DOC_ICON}</div>'
                f'<div class="r-resume-name">{r["name"]}</div>'
                f'<div class="r-resume-meta">{r.get("updated", "Updated recently")}</div>'
                f'<span class="r-badge">✓ ATS {r.get("ats_score", 0)}%</span>'
                f'</div>'
            )
