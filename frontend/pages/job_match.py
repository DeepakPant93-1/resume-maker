"""Job Match Page (Figma: job-match)"""
import re

import streamlit as st

from pages.my_resumes import all_skills, initialize_resume_data
from styles.theme import card, css, donut, html, page_header

# Keywords we look for in a job description (extend freely)
KEYWORDS = [
    "Java", "Spring Boot", "Microservices", "AWS", "Azure", "GCP", "REST APIs", "Kafka", "Docker",
    "Kubernetes", "CI/CD", "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Python", "Terraform",
    "React", "Node.js", "GraphQL", "Jenkins", "Git", "Linux",
]
DEFAULT_JD = "5+ years Java, Spring Boot, Microservices, AWS/Azure, REST APIs, databases, Docker, Kubernetes, CI/CD"

_CSS = """
.st-key-card_missing { background: #FFF5F5 !important; border-color: #FDE2E2 !important; }
.st-key-card_suggest { background: #F1FBF5 !important; border-color: #D5F2E0 !important; }
.r-bar-row { display: grid; grid-template-columns: 90px 1fr; gap: 0.75rem; align-items: center; margin: 0.45rem 0; font-size: 0.78rem; color: #6B7280; }
.r-bar { height: 7px; background: #EEF0F4; border-radius: 4px; overflow: hidden; }
.r-bar > div { height: 100%; background: #6C4FE0; border-radius: 4px; }
"""


def _find(keyword, text):
    return re.search(r"(?<![\w])" + re.escape(keyword.lower()) + r"(?![\w])", text.lower()) is not None


def analyze(jd, resume_text):
    wanted = [k for k in KEYWORDS if _find(k, jd)]
    matched = [k for k in wanted if _find(k, resume_text)]
    missing = [k for k in wanted if k not in matched]
    score = round(100 * len(matched) / len(wanted)) if wanted else 0
    return {"score": score, "wanted": wanted, "matched": matched, "missing": missing}


def _resume_text():
    d = st.session_state.resume_data
    parts = [d["profile"]["summary"], d["profile"]["job_title"], " ".join(all_skills(d))]
    parts += [j["achievements"] + " " + j["job_title"] for j in d["experience"]]
    parts += [p["technologies"] + " " + p["description"] for p in d.get("projects", [])]
    return " ".join(parts)


def render():
    initialize_resume_data()
    css(_CSS)
    page_header("Job Description Match", "Understand the match and improve your resume.")

    if "jd_result" not in st.session_state:
        st.session_state.jd_result = analyze(DEFAULT_JD, _resume_text())

    left, right = st.columns(2)
    with left:
        with card("jd"):
            html('<div class="r-card-title">Job Description</div>')
            role = st.text_input("Role", value="Senior Java Developer", key="jd_role")
            jd = st.text_area("Job description", value=DEFAULT_JD, height=110, key="jd_text")
            if st.button("✦ Analyze Match", type="primary", key="jd_analyze"):
                st.session_state.jd_result = analyze(role + " " + jd, _resume_text())
                st.rerun()

    res = st.session_state.jd_result
    with right:
        with card("score"):
            bars = "".join(
                f'<div class="r-bar-row"><span>{k}</span><div class="r-bar">'
                f'<div style="width:{100 if k in res["matched"] else 25}%"></div></div></div>'
                for k in res["wanted"][:6]
            ) or '<div class="r-muted">No known skills found in this job description.</div>'
            color = "#22A06B" if res["score"] >= 75 else "#E8A317" if res["score"] >= 50 else "#E5484D"
            html(f'<div style="display:flex;gap:1.5rem;align-items:center">'
                 f'{donut(res["score"], color, 120, "Match score")}<div style="flex:1">{bars}</div></div>')

    m, s = st.columns(2)
    with m:
        with card("missing"):
            html('<div class="r-card-title">Missing Skills</div>')
            items = "".join(f'<div style="color:#E5484D;font-size:0.85rem;margin:0.3rem 0">⊘ {k}</div>'
                            for k in res["missing"]) or '<div class="r-muted">Nothing missing — great match!</div>'
            html(items)
    with s:
        with card("suggest"):
            html('<div class="r-card-title">AI Suggestions</div>')
            tips = [f"Add {k} experience if applicable" for k in res["missing"][:3]]
            tips += ["Quantify project outcomes with numbers", "Mirror the job title in your summary"]
            html("".join(f'<div style="color:#22A06B;font-size:0.85rem;margin:0.3rem 0">✓ {t}</div>' for t in tips[:4]))
