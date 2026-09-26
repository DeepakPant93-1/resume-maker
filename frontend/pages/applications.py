"""Applications Page (Figma: applications)"""
import streamlit as st

from styles.theme import css, html, page_header

APPLICATIONS = [
    # company, role, resume used, ATS match, stage, recommended action
    ("Acme Corp", "Senior Java Developer", "Backend Tech Lead", 92, "Technical Interview", "Prepare Interview"),
    ("CloudCo", "Lead Cloud Architect", "Cloud Architect Pro", 87, "Applied", "Follow Up"),
    ("AI Labs", "AI Workflow Engineer", "AI Research Lead", 84, "Initial Screening", "Schedule Call"),
]

_CSS = """
.r-table { width: 100%; border-collapse: separate; border-spacing: 0; background: #fff;
           border: 1px solid #E6E8EF; border-radius: 12px; overflow: hidden; font-size: 0.85rem; }
.r-table th { background: #F5F3FF; color: #6C4FE0; font-weight: 600; font-size: 0.78rem;
              text-align: left; padding: 0.9rem 1.1rem; }
.r-table td { padding: 0.9rem 1.1rem; border-top: 1px solid #EEF0F4; vertical-align: middle; }
.r-table .co { font-weight: 600; color: #111827; }
.r-table .role { color: #6B7280; font-size: 0.75rem; }
.r-table .ats { color: #22A06B; font-weight: 700; }
.r-action { display: inline-block; background: #6C4FE0; color: #fff; border-radius: 6px;
            padding: 0.35rem 0.8rem; font-size: 0.75rem; font-weight: 600; }
"""


def render():
    css(_CSS)
    page_header("Job Application Tracker",
                "Connect and monitor your resume variations, matches, and pipeline status.")

    rows = "".join(
        f'<tr><td><div class="co">{company}</div><div class="role">{role}</div></td>'
        f'<td><span class="r-badge soft">{resume}</span></td>'
        f'<td class="ats">{ats}%</td>'
        f'<td><span class="r-badge grey">{stage}</span></td>'
        f'<td><span class="r-action">{action}</span></td></tr>'
        for company, role, resume, ats, stage, action in APPLICATIONS
    )
    html('<table class="r-table"><thead><tr>'
         '<th>Company / Role</th><th>Resume Used</th><th>ATS Match</th>'
         '<th>Pipeline Stage</th><th>Recommended Action</th>'
         f'</tr></thead><tbody>{rows}</tbody></table>')
