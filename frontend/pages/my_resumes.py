"""My Resumes Page - Resume Editor (Figma: resume-editor + ats-check)"""
import streamlit as st

from components.resume_preview import resume_html
from styles.theme import card, css, donut, html, page_header

SECTIONS = ["Profile", "Experience", "Education", "Skills", "Projects", "Certifications"]

_CSS = """
/* Section list looks like the sidebar nav */
[data-testid="stMain"] .st-key-card_sections button[data-testid] {
    justify-content: flex-start !important; background: transparent !important;
    border: none !important; color: #4B5563 !important; font-weight: 500 !important;
    min-height: 36px !important;
}
[data-testid="stMain"] .st-key-card_sections button p { text-align: left !important; font-size: 0.85rem !important; white-space: nowrap; }
[data-testid="stMain"] .st-key-card_sections button:hover { background: #F3F4F6 !important; }
[data-testid="stMain"] .st-key-card_sections button[data-testid="stBaseButton-primary"] {
    background: #EFEBFD !important; color: #6C4FE0 !important; font-weight: 600 !important;
}
.st-key-card_sections [data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
.st-key-card_preview { background: #EDEEF3 !important; }
.st-key-card_preview .rv { padding: 1.25rem 1.4rem; border-radius: 6px; min-height: 420px; }
/* Header action buttons */
[data-testid="stMain"] .st-key-btn_ai button[data-testid] { background: #EFEBFD !important; border: none !important; color: #6C4FE0 !important; }
[data-testid="stMain"] .st-key-btn_ats button[data-testid] { background: #E7F6EE !important; border: none !important; color: #22A06B !important; }
"""


def initialize_resume_data():
    """Sample data used by the editor, AI agent and job match pages."""
    if st.session_state.get("resume_data"):
        return
    st.session_state.resume_data = {
        "profile": {
            "full_name": "Suraj Singh",
            "job_title": "Senior Java Developer",
            "email": "suraj.singh@email.com",
            "phone": "+91 98765 43210",
            "location": "Bengaluru, India",
            "linkedin": "linkedin.com/in/surajsingh",
            "summary": "Java developer with 6+ years of experience building scalable microservices with "
                       "Spring Boot, Kafka and AWS. Passionate about clean code and mentoring.",
        },
        "experience": [
            {
                "job_title": "Senior Java Developer", "company": "TechNova Solutions",
                "start_date": "2021", "end_date": "Present", "current": True,
                "achievements": "• Led migration of a monolith to 20+ Spring Boot microservices\n"
                                "• Cut API latency by 40% with Redis caching and query tuning",
            },
            {
                "job_title": "Java Developer", "company": "CloudPeak Systems",
                "start_date": "2018", "end_date": "2021", "current": False,
                "achievements": "• Built payment APIs handling 1M+ transactions per day",
            },
        ],
        "education": [
            {"degree": "B.Tech, Computer Science", "university": "VIT University",
             "start_year": "2014", "end_year": "2018", "grade": "", "location": "Vellore, India"},
        ],
        "skills": {
            "languages": ["Java", "SQL"],
            "frameworks": ["Spring Boot", "Microservices", "Kafka", "AWS"],
            "tools": ["Docker", "Kubernetes", "MySQL"],
        },
        "projects": [
            {"name": "E-Commerce Platform",
             "description": "Built scalable microservices architecture for 100K+ daily users",
             "technologies": "Spring Boot, Kafka, AWS, Docker"},
        ],
        "certifications": [
            {"name": "AWS Certified Developer - Associate (2022)", "issuer": "Amazon Web Services"},
        ],
    }


def all_skills(data=None):
    data = data or st.session_state.resume_data
    s = data["skills"]
    return [x for x in s.get("languages", []) + s.get("frameworks", []) + s.get("tools", []) if x]


def editor_preview_html(data=None, highlight=None):
    data = data or st.session_state.resume_data
    certs = ", ".join(c["name"] for c in data.get("certifications", []) if c.get("name"))
    projects = "; ".join(p["name"] for p in data.get("projects", []) if p.get("name"))
    return resume_html(
        data["profile"], data["experience"], data["education"], all_skills(data),
        extras=[("Projects", projects), ("Certifications", certs)],
        highlight=highlight,
    )


def _split(text):
    return [s.strip() for s in text.split(",") if s.strip()]


# ---------------- Section editors ----------------

def render_profile_section():
    p = st.session_state.resume_data["profile"]
    html('<div class="r-card-title">Personal Information</div>')
    c1, c2 = st.columns(2)
    with c1:
        p["full_name"] = st.text_input("Full name", value=p["full_name"], key="ed_name")
        p["email"] = st.text_input("Email", value=p["email"], key="ed_email")
        p["location"] = st.text_input("Location", value=p["location"], key="ed_loc")
    with c2:
        p["job_title"] = st.text_input("Job title", value=p["job_title"], key="ed_title")
        p["phone"] = st.text_input("Phone", value=p["phone"], key="ed_phone")
        p["linkedin"] = st.text_input("LinkedIn", value=p["linkedin"], key="ed_li")
    html('<div class="r-card-title" style="margin-top:0.75rem">Professional Summary</div>')
    p["summary"] = st.text_area("Summary", value=p["summary"], height=110,
                                label_visibility="collapsed", key="ed_summary")


def render_experience_section():
    jobs = st.session_state.resume_data["experience"]
    html('<div class="r-card-title">Experience</div>')
    for i, job in enumerate(jobs):
        label = f"{job['job_title'] or 'New job'}" + (f" — {job['company']}" if job["company"] else "")
        with st.expander(label, expanded=(i == 0)):
            c1, c2 = st.columns(2)
            with c1:
                job["job_title"] = st.text_input("Job title", value=job["job_title"], key=f"exp_title_{i}")
                job["start_date"] = st.text_input("Start date", value=job["start_date"], key=f"exp_start_{i}")
            with c2:
                job["company"] = st.text_input("Company", value=job["company"], key=f"exp_company_{i}")
                job["end_date"] = st.text_input("End date", value=job["end_date"], key=f"exp_end_{i}",
                                                disabled=job["current"])
            job["current"] = st.checkbox("I currently work here", value=job["current"], key=f"exp_current_{i}")
            job["achievements"] = st.text_area("What did you do? (one bullet per line)", value=job["achievements"],
                                               height=100, key=f"exp_achieve_{i}")
            if st.button("Remove", key=f"remove_exp_{i}", type="tertiary"):
                jobs.pop(i)
                st.rerun()
    if st.button("\\+ Add another job", key="add_job", use_container_width=True):
        jobs.append({"job_title": "", "company": "", "start_date": "", "end_date": "",
                     "current": False, "achievements": ""})
        st.rerun()


def render_education_section():
    items = st.session_state.resume_data["education"]
    html('<div class="r-card-title">Education</div>')
    for i, edu in enumerate(items):
        with st.expander(edu["degree"] or "New education", expanded=(i == 0)):
            c1, c2 = st.columns(2)
            with c1:
                edu["degree"] = st.text_input("Degree", value=edu["degree"], key=f"edu_degree_{i}")
                edu["start_year"] = st.text_input("Start year", value=edu["start_year"], key=f"edu_start_{i}")
                edu["grade"] = st.text_input("Grade (optional)", value=edu["grade"], key=f"edu_grade_{i}")
            with c2:
                edu["university"] = st.text_input("School / University", value=edu["university"], key=f"edu_uni_{i}")
                edu["end_year"] = st.text_input("End year", value=edu["end_year"], key=f"edu_end_{i}")
                edu["location"] = st.text_input("Location", value=edu["location"], key=f"edu_loc_{i}")
            if st.button("Remove", key=f"remove_edu_{i}", type="tertiary"):
                items.pop(i)
                st.rerun()
    if st.button("\\+ Add education", key="add_education", use_container_width=True):
        items.append({"degree": "", "university": "", "start_year": "", "end_year": "",
                      "grade": "", "location": ""})
        st.rerun()


def render_skills_section():
    s = st.session_state.resume_data["skills"]
    html('<div class="r-card-title">Skills</div>')
    s["languages"] = _split(st.text_input("Languages (comma-separated)", ", ".join(s["languages"]), key="sk_lang"))
    s["frameworks"] = _split(st.text_input("Frameworks & platforms", ", ".join(s["frameworks"]), key="sk_fw"))
    s["tools"] = _split(st.text_input("Tools & databases", ", ".join(s["tools"]), key="sk_tools"))


def render_projects_section():
    items = st.session_state.resume_data["projects"]
    html('<div class="r-card-title">Projects</div>')
    for i, proj in enumerate(items):
        with st.expander(proj["name"] or "New project", expanded=(i == 0)):
            proj["name"] = st.text_input("Project name", value=proj["name"], key=f"proj_name_{i}")
            proj["description"] = st.text_area("Description", value=proj["description"], key=f"proj_desc_{i}", height=80)
            proj["technologies"] = st.text_input("Technologies used", value=proj["technologies"], key=f"proj_tech_{i}")
            if st.button("Remove", key=f"remove_proj_{i}", type="tertiary"):
                items.pop(i)
                st.rerun()
    if st.button("\\+ Add project", key="add_project", use_container_width=True):
        items.append({"name": "", "description": "", "technologies": ""})
        st.rerun()


def render_certifications_section():
    items = st.session_state.resume_data["certifications"]
    html('<div class="r-card-title">Certifications</div>')
    for i, cert in enumerate(items):
        with st.expander(cert["name"] or "New certification", expanded=(i == 0)):
            cert["name"] = st.text_input("Certification name", value=cert["name"], key=f"cert_name_{i}")
            cert["issuer"] = st.text_input("Issuer", value=cert["issuer"], key=f"cert_issuer_{i}")
            if st.button("Remove", key=f"remove_cert_{i}", type="tertiary"):
                items.pop(i)
                st.rerun()
    if st.button("\\+ Add certification", key="add_certification", use_container_width=True):
        items.append({"name": "", "issuer": ""})
        st.rerun()


EDITORS = {
    "Profile": render_profile_section,
    "Experience": render_experience_section,
    "Education": render_education_section,
    "Skills": render_skills_section,
    "Projects": render_projects_section,
    "Certifications": render_certifications_section,
}


# ---------------- ATS check modal ----------------

def _check(ok, title, sub=""):
    icon = '<span style="color:#22A06B">✓</span>' if ok else '<span style="color:#E8A317">!</span>'
    sub_html = f'<div class="r-muted" style="margin-left:1.3rem">{sub}</div>' if sub else ""
    return f'<div style="margin:0.35rem 0;font-size:0.85rem">{icon}&nbsp; {title}{sub_html}</div>'


@st.dialog("ATS check")
def ats_dialog():
    target = st.session_state.resume_data["profile"]["job_title"] or "your target role"
    html(
        '<div class="r-muted" style="margin-top:-0.75rem;margin-bottom:0.75rem">How well applicant tracking systems can read your resume</div>'
        '<div style="background:#F5F3FF;border-radius:10px;padding:0.9rem 1rem;display:flex;gap:1rem;align-items:center">'
        f'{donut(86, "#6C4FE0", 70)}'
        f'<div><div style="font-weight:600">Good — a few quick fixes left</div>'
        f'<div class="r-muted">Target role: {target}</div></div></div>'
        '<div class="r-label" style="margin-top:1rem">What\'s working</div>'
        + _check(True, "Standard section headings")
        + _check(True, "Contact details are easy to find")
        + _check(True, "Simple one-column layout")
        + '<div class="r-label" style="margin-top:0.75rem">To improve</div>'
        + _check(False, "Add missing keywords", "Kafka, AWS and Docker appear in the job but not in your resume")
        + _check(False, "Add numbers to your bullets", "Only 1 of 4 bullets shows measurable impact")
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✦ Fix these with AI", type="primary", use_container_width=True):
            st.session_state.page = "AIAgents"
            st.session_state.agent_view = "chat"
            st.rerun()
    with c2:
        if st.button("Done", use_container_width=True):
            st.rerun()


# ---------------- Page ----------------

def render():
    initialize_resume_data()
    css(_CSS)
    if "editor_section" not in st.session_state:
        st.session_state.editor_section = "Profile"

    head, actions = st.columns([6, 4], vertical_alignment="center")
    with head:
        page_header("Resume Editor", "Edit content while keeping a live preview.")
    with actions:
        _, a1, a2, a3 = st.columns([1, 1.3, 1.2, 0.9])
        with a1:
            if st.button("✦ AI Improve", key="btn_ai", use_container_width=True):
                st.session_state.page = "AIAgents"
                st.session_state.agent_view = "chat"
                st.rerun()
        with a2:
            if st.button("ATS Check", key="btn_ats", use_container_width=True):
                ats_dialog()
        with a3:
            if st.button("Save", key="btn_save", type="primary", use_container_width=True):
                st.toast("Resume saved", icon=":material/check_circle:")

    col_sections, col_content, col_preview = st.columns([1.4, 2.6, 2.4])

    with col_sections:
        with card("sections"):
            html('<div class="r-card-title">Sections</div>')
            for name in SECTIONS:
                active = st.session_state.editor_section == name
                if st.button(name, key=f"sec_{name}", type="primary" if active else "secondary",
                             use_container_width=True):
                    st.session_state.editor_section = name
                    st.rerun()

    with col_content:
        with card("editor"):
            EDITORS[st.session_state.editor_section]()

    with col_preview:
        with card("preview"):
            html('<div class="r-card-title">Live Preview</div>')
            html(editor_preview_html())
