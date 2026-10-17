"""Login page: log in to an existing account or create one. Shown instead of the app until someone is signed in."""
import streamlit as st

from styles.theme import card, css, html
from utils import auth
from utils.api_client import ApiError, login, register

MIN_PASSWORD_LENGTH = 8  # the backend enforces the same rule

_CSS = """
section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"] { display: none !important; }
.r-login-brand { text-align: center; margin: 3rem 0 0.4rem; font-size: 1.9rem; font-weight: 700; }
.r-login-sub { text-align: center; color: #6B7280; margin-bottom: 1.5rem; }
"""


def _finish(response):
    auth.sign_in(response)
    st.rerun()


def _render_login():
    with st.form("login_form", border=False):
        email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
    if not submitted:
        return
    if not email.strip() or not password:
        st.error("Please enter your email and password.")
        return
    try:
        with st.spinner("Logging in..."):
            response = login(email, password)
    except ApiError as e:
        st.error(str(e))
        return
    _finish(response)


def _render_register():
    with st.form("register_form", border=False):
        name = st.text_input("Name", key="register_name", placeholder="Your full name")
        email = st.text_input("Email", key="register_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="register_password",
                                 help=f"At least {MIN_PASSWORD_LENGTH} characters")
        confirm = st.text_input("Confirm password", type="password", key="register_confirm")
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
    if not submitted:
        return
    if not email.strip():
        st.error("Please enter your email.")
    elif len(password) < MIN_PASSWORD_LENGTH:
        st.error(f"The password must be at least {MIN_PASSWORD_LENGTH} characters.")
    elif password != confirm:
        st.error("The two passwords do not match.")
    else:
        try:
            with st.spinner("Creating your account..."):
                response = register(name, email, password)
        except ApiError as e:
            st.error(str(e))
            return
        _finish(response)


def render():
    css(_CSS)
    _, middle, _ = st.columns([1, 1.3, 1])
    with middle:
        html('<div class="r-login-brand">ResuAI</div>'
             '<div class="r-login-sub">Log in to build and tailor your resumes</div>')
        notice = st.session_state.pop("login_notice", None)
        if notice:
            st.info(notice)
        with card("login"):
            log_in, create = st.tabs(["Log in", "Create account"])
            with log_in:
                _render_login()
            with create:
                _render_register()
