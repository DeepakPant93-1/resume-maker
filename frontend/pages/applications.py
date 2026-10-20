"""Applications Page (Figma: applications)"""
from html import escape

import streamlit as st

from styles.theme import css, html, page_header
from utils.api_client import ApiError, list_applications, list_resumes

STAGE_LABELS = {"APPLIED": "Applied", "SCREENING": "Initial Screening", "INTERVIEW": "Interview",
                "OFFER": "Offer", "REJECTED": "Rejected"}

_CSS = """
.r-table { width: 100%; border-collapse: separate; border-spacing: 0; background: #fff;
           border: 1px solid #E6E8EF; border-radius: 12px; overflow: hidden; font-size: 0.85rem; }
.r-table th { background: #F5F3FF; color: #6C4FE0; font-weight: 600; font-size: 0.78rem;
              text-align: left; padding: 0.9rem 1.1rem; }
.r-table td { padding: 0.9rem 1.1rem; border-top: 1px solid #EEF0F4; vertical-align: middle; }
.r-table .co { font-weight: 600; color: #111827; }
.r-table .role { color: #6B7280; font-size: 0.75rem; }
.r-table .ats { color: #22A06B; font-weight: 700; }
"""


def render():
    css(_CSS)
    page_header("Job Application Tracker",
                "Connect and monitor your resume variations, matches, and pipeline status.")

    try:
        applications = list_applications()
        resumes = {r["id"]: r for r in list_resumes()}
    except ApiError as e:
        st.warning(f"Could not load your applications: {e}")
        return
    if not applications:
        html('<div class="r-card r-muted">No applications tracked yet.</div>')
        return

    def _row(app):
        resume = resumes.get(app.get("resumeId")) or {}
        ats = resume.get("ats_score")
        return (
            f'<tr><td><div class="co">{escape(app["company"])}</div>'
            f'<div class="role">{escape(app["role"])}</div></td>'
            f'<td><span class="r-badge soft">{escape(resume.get("title") or "—")}</span></td>'
            f'<td class="ats">{f"{ats}%" if ats is not None else "—"}</td>'
            f'<td><span class="r-badge grey">{STAGE_LABELS.get(app["stage"], app["stage"])}</span></td></tr>'
        )

    rows = "".join(_row(app) for app in applications)
    html('<table class="r-table"><thead><tr>'
         '<th>Company / Role</th><th>Resume Used</th><th>ATS Match</th><th>Pipeline Stage</th>'
         f'</tr></thead><tbody>{rows}</tbody></table>')
