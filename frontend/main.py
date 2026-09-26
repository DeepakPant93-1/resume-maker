"""
Main Frontend Application
Streamlit configuration and routing
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from styles.theme import apply_theme, html
from pages import dashboard, create_resume, my_resumes, job_match, templates, ai_agents, applications, settings

# Accent colour per menu item (icon tile, hover tint)
NAV_COLORS = {
    "Dashboard": "#6C4FE0", "MyResumes": "#3B82F6", "CreateResume": "#10B981", "JobMatch": "#F59E0B",
    "Templates": "#EC4899", "AIAgents": "#8B5CF6", "Applications": "#06B6D4", "Settings": "#64748B",
}

# (label, page key, Material icon) - order matches the Figma sidebar
NAV_ITEMS = [
    ("Dashboard", "Dashboard", ":material/dashboard:"),
    ("My Resumes", "MyResumes", ":material/description:"),
    ("Create Resume", "CreateResume", ":material/add_circle:"),
    ("Job Match", "JobMatch", ":material/work:"),
    ("Templates", "Templates", ":material/grid_view:"),
    ("AI Agents", "AIAgents", ":material/auto_awesome:"),
    ("Applications", "Applications", ":material/send:"),
    ("Settings", "Settings", ":material/settings:"),
]

PAGES = {
    "Dashboard": dashboard,
    "MyResumes": my_resumes,
    "CreateResume": create_resume,
    "JobMatch": job_match,
    "Templates": templates,
    "AIAgents": ai_agents,
    "Applications": applications,
    "Settings": settings,
}


def initialize_app():
    """Initialize Streamlit app configuration"""
    st.set_page_config(
        page_title="ResuAI - Resume Builder",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()


def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "user" not in st.session_state:
        st.session_state.user = {"name": "Suraj Singh", "role": "Technical Lead"}
    if "resumes" not in st.session_state:
        st.session_state.resumes = [
            {"name": "Backend Developer", "ats_score": 92, "updated": "Updated recently"},
            {"name": "AI Engineer", "ats_score": 87, "updated": "Updated recently"},
            {"name": "Cloud Architect", "ats_score": 81, "updated": "Updated recently"},
        ]


def go_to(page_key: str):
    """Switch page from anywhere (e.g. a 'Choose Template' button on the dashboard)."""
    st.session_state.page = page_key
    st.rerun()


def _nav_css(current):
    rules = [
        # brand in gradient text
        ".r-brand { background: linear-gradient(90deg,#6C4FE0,#EC4899); -webkit-background-clip: text;"
        " background-clip: text; color: transparent !important; }",
        ".r-brand-dot { background: linear-gradient(135deg,#6C4FE0,#EC4899) !important; box-shadow: none !important; }",
        # soft purple glow at the top of the sidebar
        'section[data-testid="stSidebar"] { background: linear-gradient(180deg,#F7F4FF 0%,#FFFFFF 220px) !important; }',
        '[data-testid="stSidebar"] .stButton button { transition: background .15s ease, transform .15s ease; }',
        '[data-testid="stSidebar"] .stButton button:hover { transform: translateX(3px); }',
    ]
    for key, color in NAV_COLORS.items():
        sel = f'[data-testid="stSidebar"] .st-key-nav_{key} .stButton button[data-testid]'
        rules.append(f'{sel} [data-testid="stIconMaterial"] {{ color: {color} !important; background: {color}1F;'
                     f' border-radius: 7px; padding: 4px; font-size: 1.05rem !important; }}')
        rules.append(f'{sel}:hover {{ background: {color}14 !important; color: {color} !important; }}')
    active = NAV_COLORS.get(current, "#6C4FE0")
    sel = f'[data-testid="stSidebar"] .st-key-nav_{current} .stButton button[data-testid]'
    rules.append(f'{sel}, {sel}:hover {{ background: linear-gradient(135deg,{active},{active}CC) !important;'
                 f' color: #FFFFFF !important; box-shadow: 0 4px 12px {active}40 !important; }}')
    rules.append(f'{sel} [data-testid="stIconMaterial"] {{ color: #FFFFFF !important; background: #FFFFFF33 !important; }}')
    rules.append(f'{sel} p {{ color: #FFFFFF !important; font-weight: 600 !important; }}')
    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)


def render_sidebar():
    """Single-column nav with coloured icons and a gradient active item."""
    current = st.session_state.page
    with st.sidebar:
        _nav_css(current)
        html(
            '<div class="r-brand"><span class="r-brand-dot"></span>ResuAI</div>'
            '<div class="r-nav-label">WORKSPACE</div>'
        )
        for label, key, icon in NAV_ITEMS:
            clicked = st.button(
                label,
                key=f"nav_{key}",
                icon=icon,
                type="primary" if current == key else "secondary",
                use_container_width=True,
            )
            if clicked:
                if key == "CreateResume":
                    st.session_state.builder_mode = None   # always open the start screen
                if key == "AIAgents":
                    st.session_state.agent_view = "workspace"
                go_to(key)


def render_topbar():
    """White top bar: search on the left, user on the right."""
    user = st.session_state.user
    initials = "".join(part[0] for part in user["name"].split()[:2]).upper()
    with st.container(key="topbar"):
        left, _, right = st.columns([4, 5, 3], vertical_alignment="center")
        with left:
            st.text_input(
                "Search",
                placeholder="Search resumes, jobs, templates",
                label_visibility="collapsed",
                key="global_search",
            )
        with right:
            html(
                f'<div class="r-user"><div class="r-avatar">{initials}</div>'
                f'<div><div class="r-user-name">{user["name"]}</div>'
                f'<div class="r-user-role">{user["role"]}</div></div></div>'
            )


def in_focus_mode():
    """The resume builder wizard is full-screen in Figma (no sidebar / search bar)."""
    page = st.session_state.page
    return ((page == "CreateResume" and st.session_state.get("builder_mode") == "builder")
            or (page == "AIAgents" and st.session_state.get("agent_view") == "chat"))


def render_page():
    PAGES.get(st.session_state.page, dashboard).render()


def run():
    """Main application entry point"""
    initialize_app()
    init_state()
    render_sidebar()
    if not in_focus_mode():
        render_topbar()
    render_page()


if __name__ == "__main__":
    run()
