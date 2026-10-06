"""Client for the Spring Boot resume API (backend/resumemaker)."""
import os

import requests

from utils import auth

API_URL = os.environ.get("RESUMEMAKER_API_URL", "http://localhost:8080")
UPLOAD_TIMEOUT_SECONDS = 60
TIMEOUT_SECONDS = 15

# The sections the editor keeps in session state, in the shape the backend expects.
RESUME_SECTIONS = ("profile", "experience", "education", "skills", "projects", "certifications")


class ApiError(Exception):
    """Raised with a user-readable message when a backend call fails. `status_code` is the HTTP status, if any."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def _call(method, path, timeout=TIMEOUT_SECONDS, on_bad_request=None, public=False, **kwargs):
    """Call the backend and return its JSON; any failure becomes an ApiError with a message fit for the UI.

    Every call carries the login token, except `public` ones (login, register).
    """
    login_token = None if public else auth.token()
    if login_token:
        kwargs["headers"] = {"Authorization": f"Bearer {login_token}"}
    try:
        resp = requests.request(method, f"{API_URL}{path}", timeout=timeout, **kwargs)
    except requests.RequestException:
        raise ApiError(f"Could not reach the backend at {API_URL}. Is it running?")
    if resp.ok:
        return resp.json()
    if resp.status_code == 401 and not public:
        # The token expired or is no longer valid: forget it and send the user back to the login page.
        import streamlit as st

        auth.sign_out("Your session has expired. Please log in again.")
        st.rerun()
    if resp.status_code == 400 and on_bad_request:
        raise ApiError(on_bad_request, 400)
    try:
        message = resp.json().get("message")
    except ValueError:
        message = None
    raise ApiError(message or f"The backend returned an error (HTTP {resp.status_code}).", resp.status_code)


def login(email, password):
    """Log in; returns {token, expires_at, user}. A wrong email or password raises ApiError."""
    return _call("POST", "/api/auth/login", public=True, json={"email": email, "password": password})


def whoami(login_token):
    """Who a saved login token belongs to: {id, email, name}. A 401 ApiError means the token is no longer valid."""
    return _call("GET", "/api/auth/me", public=True, headers={"Authorization": f"Bearer {login_token}"})


def register(name, email, password):
    """Create an account and log in; returns the same as login()."""
    return _call("POST", "/api/auth/register", public=True,
                 json={"name": name, "email": email, "password": password})


def upload_resume(filename, content):
    """POST a PDF to the backend; returns the parsed, saved resume (with its id) as a dict."""
    return _call(
        "POST", "/api/resumes/upload", timeout=UPLOAD_TIMEOUT_SECONDS,
        files={"file": (filename, content, "application/pdf")},
        on_bad_request="The backend could not read this file. Please upload a text-based PDF.",
    )


def save_resume(resume_id, data):
    """Save the editor's resume: update it if it already has a backend id, otherwise create it."""
    payload = {section: data.get(section) for section in RESUME_SECTIONS}
    if resume_id:
        return _call("PUT", f"/api/resumes/{resume_id}", json=payload)
    return _call("POST", "/api/resumes", json=payload)


def list_resumes():
    """Every saved resume as dashboard rows: {id, title, ats_score, updated_at}, most recently saved first."""
    return _call("GET", "/api/resumes")


def get_resume(resume_id):
    """One saved resume, in the shape to_editor_data() expects."""
    return _call("GET", f"/api/resumes/{resume_id}")


def check_ats(data, job_description=None):
    """Score the editor's resume for ATS (saved or not). Returns {score, against_job, components, suggestions}."""
    payload = {section: data.get(section) for section in RESUME_SECTIONS}
    return _call("POST", "/api/ats", json={"resume": payload, "job_description": job_description or None})


def start_run(resume_id, job_description):
    """Start an AI run on a saved resume (optionally tailored to a job description); returns {run_id, status}."""
    return _call("POST", f"/api/resumes/{resume_id}/runs", json={"job_description": job_description or None})


def get_run(run_id):
    """The run record: status (running / waiting_for_user / completed / failed), question, output, state."""
    return _call("GET", f"/api/runs/{run_id}")


def answer_run(run_id, answer):
    """Give a run that is waiting for the user its answer, so it continues."""
    return _call("POST", f"/api/runs/{run_id}/resume", json={"answer": answer})


def to_editor_data(resume):
    """Fill gaps (null fields from the parser) so the editor widgets always get strings and lists."""
    profile = resume.get("profile") or {}
    skills = resume.get("skills") or {}
    return {
        "profile": {k: profile.get(k) or "" for k in
                    ("full_name", "job_title", "email", "phone", "location", "linkedin", "summary")},
        "experience": [
            {**{k: j.get(k) or "" for k in ("job_title", "company", "start_date", "end_date", "achievements")},
             "current": bool(j.get("current"))}
            for j in resume.get("experience") or []
        ],
        "education": [
            {k: e.get(k) or "" for k in ("degree", "university", "start_year", "end_year", "grade", "location")}
            for e in resume.get("education") or []
        ],
        "skills": {k: skills.get(k) or [] for k in ("languages", "frameworks", "tools")},
        "projects": [
            {k: p.get(k) or "" for k in ("name", "description", "technologies")}
            for p in resume.get("projects") or []
        ],
        "certifications": [
            {k: c.get(k) or "" for k in ("name", "issuer")} for c in resume.get("certifications") or []
        ],
    }
