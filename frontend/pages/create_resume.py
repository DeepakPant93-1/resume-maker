"""Create Resume Page - start screen + 6-step builder (Figma: create-resume, wizard-1..6)"""
import streamlit as st

from components.resume_preview import TEMPLATES, resume_html, template_thumb
from styles.theme import card, css, donut, html, page_header

STEPS = ["Personal info", "Experience", "Education", "Skills", "Template", "Preview"]
SUGGESTED_SKILLS = ["Redis", "CI/CD", "Terraform", "REST APIs", "JUnit"]

_SPARK = ('<div style="width:34px;height:34px;border-radius:8px;background:#EFEBFD;color:#6C4FE0;'
          'display:flex;align-items:center;justify-content:center;font-size:1rem">✦</div>')

_CSS = """
.r-method-title { font-size: 1rem; font-weight: 600; color: #111827; margin: 0.9rem 0 0.25rem; }
.r-method-desc { font-size: 0.82rem; color: #6B7280; min-height: 2.6rem; margin-bottom: 0.6rem; }
.r-flow { display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.75rem; }
.r-flow-item { background: #fff; border: 1px solid #E6E8EF; border-radius: 10px; padding: 0.8rem 0.9rem; }
.r-flow-num { color: #6C4FE0; font-weight: 700; font-size: 0.85rem; }
.r-flow-name { font-weight: 600; font-size: 0.85rem; color: #111827; margin-top: 0.35rem; }
"""

_BUILDER_CSS = """
/* Full-screen wizard: hide the app sidebar */
section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] { display: none !important; }
.r-wiz-bar { display: flex; justify-content: space-between; align-items: center; }
.r-wiz-brand { font-weight: 700; color: #6C4FE0; font-size: 1.05rem; }
.stepper { display: flex; margin: 0.5rem 0 1rem; }
.stp { flex: 1; text-align: center; position: relative; }
.stp:before { content: ""; position: absolute; top: 13px; left: -50%; width: 100%; height: 2px; background: #E6E8EF; }
.stp:first-child:before { display: none; }
.stp.done:before, .stp.active:before { background: #6C4FE0; }
.stp-dot { position: relative; z-index: 1; width: 26px; height: 26px; border-radius: 50%; margin: 0 auto;
           border: 1.5px solid #D1D5DB; background: #fff; color: #9CA3AF; font-size: 0.72rem;
           display: flex; align-items: center; justify-content: center; font-weight: 600; }
.stp.active .stp-dot { border-color: #6C4FE0; color: #6C4FE0; box-shadow: 0 0 0 4px #EFEBFD; }
.stp.done .stp-dot { background: #6C4FE0; border-color: #6C4FE0; color: #fff; }
.stp-label { font-size: 0.72rem; color: #9CA3AF; margin-top: 0.35rem; }
.stp.active .stp-label, .stp.done .stp-label { color: #111827; font-weight: 600; }
.st-key-card_wizpreview .rv { border: 1px solid #E6E8EF; border-radius: 6px; padding: 1rem 1.1rem; }
.r-ready li { list-style: none; margin: 0.35rem 0; font-size: 0.85rem; }
"""


def initialize_builder():
    if "builder_mode" not in st.session_state:
        st.session_state.builder_mode = None
    if "builder_step" not in st.session_state:
        st.session_state.builder_step = 1
    if "new_resume" not in st.session_state:
        st.session_state.new_resume = {
            "name": "New Resume",
            "personal_info": {"full_name": "", "job_title": "", "email": "", "phone": "",
                              "location": "", "linkedin": "", "summary": ""},
            "experience": [],
            "education": [],
            "skills": [],
            "languages": "",
            "certifications": "",
            "template": st.session_state.get("selected_template", "Modern"),
            "ats_score": 0,
        }


def _go_step(n):
    st.session_state.builder_step = n
    st.rerun()


def _nav(back_label, back_step, next_label=None, next_step=None, can_next=True):
    """Bottom buttons of the form card."""
    st.write("")
    left, _, right = st.columns([1, 2, 2])
    with left:
        if st.button(back_label, key=f"back_{st.session_state.builder_step}", use_container_width=True):
            if back_step is None:
                st.session_state.builder_mode = None
                st.rerun()
            _go_step(back_step)
    with right:
        if next_label and st.button(f"{next_label} →", type="primary", use_container_width=True,
                                    disabled=not can_next, key=f"next_{st.session_state.builder_step}"):
            _go_step(next_step)


# ---------------- Start screen ----------------

def render_creation_methods():
    css(_CSS)
    page_header("Create your resume", "Choose how you want to start.")

    methods = [
        ("upload", "Upload Existing Resume", "Extract your experience, skills and education automatically.",
         "Upload Resume", "primary"),
        ("builder", "Start From Scratch", "Build your resume step by step with guided fields.",
         "Start Building", "secondary"),
        ("ai_generate", "Generate With AI", "Tell AI about your target role and generate a first draft.",
         "Generate With AI", "primary"),
    ]
    for col, (mode, title, desc, btn, kind) in zip(st.columns(3), methods):
        with col:
            with card(f"method_{mode}"):
                html(f'{_SPARK}<div class="r-method-title">{title}</div><div class="r-method-desc">{desc}</div>')
                if st.button(btn, key=f"method_btn_{mode}", type=kind):
                    if mode == "ai_generate":          # Figma: opens the AI Resume Agent
                        st.session_state.page = "AIAgents"
                        st.session_state.agent_view = "chat"
                        st.session_state.agent_back = "CreateResume"
                        st.rerun()
                    st.session_state.builder_mode = mode
                    st.session_state.builder_step = 1
                    st.rerun()

    html('<div class="r-card-title" style="margin-top:1.5rem">Recommended flow</div>')
    items = "".join(
        f'<div class="r-flow-item"><div class="r-flow-num">{i}.</div>'
        f'<div class="r-flow-name">{name}</div><div class="r-muted">AI assisted</div></div>'
        for i, name in enumerate(STEPS, 1)
    )
    html(f'<div class="r-flow">{items}</div>')


# ---------------- Builder steps ----------------

def step_personal(r):
    p = r["personal_info"]
    html('<div class="r-card-title">Personal information</div>')
    c1, c2 = st.columns(2)
    with c1:
        p["full_name"] = st.text_input("Full name", p["full_name"], placeholder="Suraj Singh", key="w_name")
        p["email"] = st.text_input("Email", p["email"], placeholder="you@email.com", key="w_email")
        p["location"] = st.text_input("Location", p["location"], placeholder="Bengaluru, India", key="w_loc")
    with c2:
        p["job_title"] = st.text_input("Job title", p["job_title"], placeholder="Senior Java Developer", key="w_title")
        p["phone"] = st.text_input("Phone", p["phone"], placeholder="+91 98765 43210", key="w_phone")
        p["linkedin"] = st.text_input("LinkedIn (optional)", p["linkedin"], placeholder="linkedin.com/in/you", key="w_li")
    lab, ai = st.columns([4, 1])
    with lab:
        html('<div style="font-size:0.875rem;margin-top:0.4rem">Professional summary</div>')
    with ai:
        if st.button("✦ Write with AI", key="chip_write_ai", use_container_width=True):
            st.toast("Connect your AI backend to generate a summary.", icon=":material/auto_awesome:")
    p["summary"] = st.text_area("Professional summary", p["summary"], height=110, label_visibility="collapsed",
                                placeholder="Describe your background in 2–3 sentences…", key="w_summary")
    _nav("Cancel", None, "Next: Experience", 2, can_next=bool(p["full_name"].strip()))
    if not p["full_name"].strip():
        st.caption("Add your full name to continue.")


def step_experience(r):
    html('<div class="r-card-title">Work experience</div>')
    if not r["experience"]:
        r["experience"].append({"job_title": "", "company": "", "start_date": "", "end_date": "",
                                "current": False, "achievements": ""})
    for i, job in enumerate(r["experience"]):
        label = f"Job {i + 1}" + (f": {job['job_title']} — {job['company']}" if job["job_title"] else "")
        with st.expander(label, expanded=(i == len(r["experience"]) - 1)):
            c1, c2 = st.columns(2)
            with c1:
                job["job_title"] = st.text_input("Job title", job["job_title"], key=f"w_exp_title_{i}")
            with c2:
                job["company"] = st.text_input("Company", job["company"], key=f"w_exp_co_{i}")
            d1, d2, d3 = st.columns([1, 1, 1.2], vertical_alignment="bottom")
            with d1:
                job["start_date"] = st.text_input("Start date", job["start_date"], placeholder="Jun 2021", key=f"w_exp_s_{i}")
            with d2:
                job["end_date"] = st.text_input("End date", job["end_date"], placeholder="Present",
                                                disabled=job["current"], key=f"w_exp_e_{i}")
            with d3:
                job["current"] = st.checkbox("I currently work here", job["current"], key=f"w_exp_cur_{i}")
            job["achievements"] = st.text_area("What did you do?", job["achievements"], height=100,
                                               placeholder="• Led migration of a monolith to 20+ microservices",
                                               key=f"w_exp_a_{i}")
            if len(r["experience"]) > 1 and st.button("Remove job", key=f"w_exp_rm_{i}", type="tertiary"):
                r["experience"].pop(i)
                st.rerun()
    if st.button("\\+ Add another job", key="w_add_job", use_container_width=True):
        r["experience"].append({"job_title": "", "company": "", "start_date": "", "end_date": "",
                                "current": False, "achievements": ""})
        st.rerun()
    _nav("Back", 1, "Next: Education", 3)


def step_education(r):
    html('<div class="r-card-title">Education</div>')
    if not r["education"]:
        r["education"].append({"degree": "", "university": "", "start_year": "", "end_year": "",
                               "grade": "", "location": ""})
    for i, edu in enumerate(r["education"]):
        with st.expander(edu["degree"] or f"Education {i + 1}", expanded=(i == len(r["education"]) - 1)):
            c1, c2 = st.columns(2)
            with c1:
                edu["degree"] = st.text_input("Degree", edu["degree"], placeholder="B.Tech, Computer Science", key=f"w_edu_d_{i}")
            with c2:
                edu["university"] = st.text_input("School / University", edu["university"], key=f"w_edu_u_{i}")
            y1, y2, g = st.columns([1, 1, 2])
            with y1:
                edu["start_year"] = st.text_input("Start year", edu["start_year"], key=f"w_edu_s_{i}")
            with y2:
                edu["end_year"] = st.text_input("End year", edu["end_year"], key=f"w_edu_e_{i}")
            with g:
                edu["grade"] = st.text_input("Grade (optional)", edu["grade"], key=f"w_edu_g_{i}")
            edu["location"] = st.text_input("Location", edu["location"], key=f"w_edu_l_{i}")
    if st.button("\\+ Add education", key="w_add_edu", use_container_width=True):
        r["education"].append({"degree": "", "university": "", "start_year": "", "end_year": "",
                               "grade": "", "location": ""})
        st.rerun()
    r["certifications"] = st.text_input("Certifications (optional)", r["certifications"],
                                        placeholder="AWS Certified Developer – Associate (2022)", key="w_certs")
    _nav("Back", 2, "Next: Skills", 4)


def _add_skill(skill):
    current = st.session_state.get("w_skills", [])
    if skill not in current:
        st.session_state.w_skills = current + [skill]


def step_skills(r):
    html('<div class="r-card-title">Skills</div>')
    if "w_skills" not in st.session_state:
        st.session_state.w_skills = list(r["skills"])
    options = sorted(set(st.session_state.w_skills) | set(SUGGESTED_SKILLS))
    st.multiselect("Add your skills", options, key="w_skills", accept_new_options=True,
                   placeholder="Type a skill and press Enter")
    r["skills"] = list(st.session_state.w_skills)

    html('<div style="font-size:0.85rem;font-weight:600;margin:0.75rem 0 0.4rem">✦ Suggested by AI for your role</div>')
    remaining = [s for s in SUGGESTED_SKILLS if s not in r["skills"]]
    if remaining:
        for col, skill in zip(st.columns(len(remaining) + 1), remaining):
            with col:
                st.button(f"\\+ {skill}", key=f"chip_sug_{skill}", on_click=_add_skill, args=(skill,))
    else:
        st.caption("All suggestions added.")

    r["languages"] = st.text_input("Languages", r["languages"], placeholder="English — Fluent, Hindi — Native",
                                   key="w_langs")
    _nav("Back", 3, "Next: Template", 5, can_next=bool(r["skills"]))
    if not r["skills"]:
        st.caption("Add at least one skill to continue.")


def step_template(r):
    html('<div class="r-card-title">Choose a template</div>')
    for col, (name, desc, accent, style, _tags) in zip(st.columns(3), TEMPLATES[:3]):
        with col:
            selected = r["template"] == name
            with card(f"wiztpl_{name}"):
                html(template_thumb(accent, style, 140)
                     + f'<div style="font-weight:600;margin-top:0.6rem">{name}</div>'
                       f'<div class="r-muted">{desc}</div>')
                if st.button("✓ Selected" if selected else "Select", key=f"w_tpl_{name}",
                             type="primary" if selected else "secondary", use_container_width=True):
                    r["template"] = name
                    st.rerun()
    css(f".st-key-card_wiztpl_{r['template']} {{ border: 1.5px solid #6C4FE0 !important; }}")
    if st.button("Browse all 6 templates →", type="tertiary", key="w_browse"):
        st.session_state.page = "Templates"
        st.rerun()
    _nav("Back", 4, "Next: Preview", 6)


def _preview(r, placeholders=True):
    return resume_html(
        r["personal_info"], r["experience"], r["education"], r["skills"],
        extras=[("Certifications", r["certifications"]), ("Languages", r["languages"])],
        show_placeholders=placeholders,
    )


def _save_to_editor(r):
    """Copy the wizard result into the editor + resume list."""
    st.session_state.resume_data = {
        "profile": dict(r["personal_info"]),
        "experience": [dict(j) for j in r["experience"] if j["job_title"] or j["company"]],
        "education": [dict(e) for e in r["education"] if e["degree"] or e["university"]],
        "skills": {"languages": [], "frameworks": list(r["skills"]), "tools": []},
        "projects": [],
        "certifications": [{"name": r["certifications"], "issuer": ""}] if r["certifications"] else [],
    }
    title = r["personal_info"]["job_title"] or r["name"]
    st.session_state.resumes.append({"name": title, "ats_score": 92, "updated": "Updated just now"})


def step_preview(r):
    left, right = st.columns([3, 2])
    with left:
        with card("wizfinal"):
            html(_preview(r, placeholders=False))
    with right:
        with card("wizready"):
            html(
                '<div style="display:flex;gap:0.75rem;align-items:center">'
                '<div style="width:36px;height:36px;border-radius:50%;background:#E7F6EE;color:#22A06B;'
                'display:flex;align-items:center;justify-content:center;font-weight:700">✓</div>'
                f'<div><div style="font-weight:600">Your resume is ready</div>'
                f'<div class="r-muted">{r["template"]} template · 1 page</div></div></div>'
                '<div style="background:#F5F3FF;border-radius:10px;padding:0.9rem 1rem;margin:1rem 0;'
                'display:flex;gap:0.75rem;align-items:center">'
                '<div style="font-size:1.8rem;font-weight:700;color:#6C4FE0">92</div>'
                '<div><div style="font-weight:600;font-size:0.9rem">ATS score</div>'
                '<div class="r-muted">Great! Recruiter systems can read it easily.</div></div></div>'
                '<ul class="r-ready" style="padding:0">'
                '<li><span style="color:#22A06B">✓</span>&nbsp; All key sections filled</li>'
                '<li><span style="color:#22A06B">✓</span>&nbsp; Keywords match your job title</li>'
                '<li><span style="color:#22A06B">✓</span>&nbsp; Fits on one page</li></ul>'
            )
            st.write("")
            if st.button("Open in editor", type="primary", use_container_width=True, key="w_open_editor"):
                _save_to_editor(r)
                st.session_state.builder_mode = None
                st.session_state.builder_step = 1
                st.session_state.page = "MyResumes"
                del st.session_state["new_resume"]
                st.session_state.pop("w_skills", None)
                st.rerun()
            d, b = st.columns(2)
            with d:
                name = (r["personal_info"]["full_name"] or "resume").replace(" ", "_")
                st.download_button("Download", data=_preview(r, False), file_name=f"{name}.html",
                                   mime="text/html", use_container_width=True, key="w_download")
            with b:
                if st.button("Back", use_container_width=True, key="w_back_6"):
                    _go_step(5)


STEP_RENDERERS = {1: step_personal, 2: step_experience, 3: step_education,
                  4: step_skills, 5: step_template, 6: step_preview}


def render_builder():
    css(_BUILDER_CSS)
    r = st.session_state.new_resume
    step = st.session_state.builder_step

    with st.container(key="topbar"):
        html(f'<div class="r-wiz-bar"><span class="r-wiz-brand">ResuAI</span>'
             f'<span class="r-muted">Step {step} of {len(STEPS)}</span></div>')

    if st.button("← Exit to Create Resume", type="tertiary", key="w_exit"):
        st.session_state.builder_mode = None
        st.rerun()
    html('<h1 class="r-page-title" style="font-size:1.4rem">Build your resume</h1>')

    dots = "".join(
        f'<div class="stp {"done" if i < step else "active" if i == step else ""}">'
        f'<div class="stp-dot">{"✓" if i < step else i}</div><div class="stp-label">{name}</div></div>'
        for i, name in enumerate(STEPS, 1)
    )
    html(f'<div class="stepper">{dots}</div>')

    if step == 6:
        step_preview(r)
        return

    form, preview = st.columns([3, 2])
    with form:
        with card("wizform"):
            STEP_RENDERERS[step](r)
    with preview:
        with card("wizpreview"):
            html('<div style="display:flex;justify-content:space-between;margin-bottom:0.6rem">'
                 '<span style="font-weight:600">Live preview</span>'
                 '<span class="r-muted">Updates as you type</span></div>')
            html(_preview(r))


# ---------------- Other modes ----------------

def _back_to_start():
    if st.button("← Back", type="tertiary", key="mode_back"):
        st.session_state.builder_mode = None
        st.rerun()


def render_upload():
    _back_to_start()
    page_header("Upload your resume", "We'll extract your experience, skills and education.")
    with card("upload"):
        uploaded = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])
        if uploaded is not None:
            st.success(f"File uploaded: {uploaded.name}")
            st.info("Parsing needs the backend integration.")


def render_ai_generate():
    _back_to_start()
    page_header("Generate with AI", "Tell AI about your target role and get a first draft.")
    with card("aigen"):
        role = st.text_input("What role are you targeting?", placeholder="e.g. Senior Backend Engineer")
        st.text_area("Anything to highlight? (optional)", placeholder="Years of experience, key projects, skills…")
        if st.button("Generate resume draft", type="primary", disabled=not role):
            st.info("Generating needs the AI backend integration.")


def render():
    initialize_builder()
    mode = st.session_state.builder_mode
    if mode is None:
        render_creation_methods()
    elif mode == "builder":
        render_builder()
    elif mode == "upload":
        render_upload()
    elif mode == "ai_generate":
        render_ai_generate()
