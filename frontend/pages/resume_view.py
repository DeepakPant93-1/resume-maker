"""View a saved resume in a template: the templates on the left, the resume as a PDF on the right with its download
button in the toolbar.

Opened from the dashboard's View button, which sets `view_resume` ({id, title}); not a sidebar page. The PDF is
built by the backend (utils/api_client.download_resume); this page only shows it.
"""
import html as _html
import io

import streamlit as st
from pypdf import PdfReader

from styles.theme import css, html
from utils.api_client import ApiError, download_resume, list_templates

PDF_MIME = "application/pdf"
DEFAULT_TEMPLATE = "classic"
PANE_HEIGHT = 820

_CSS = """
section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"] { display: none !important; }
.st-key-rv_files, .st-key-rv_preview {
  background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px; }
.st-key-rv_files { background: #F7F7FB; }
.r-rv-title { font-weight: 700; font-size: 1.05rem; color: #111827; margin: 4px 0 0; }
.r-rv-label { font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: #6B7280; margin: 14px 0 4px; }
.r-rv-pages { color: #6B7280; font-size: .85rem; white-space: nowrap; }
.r-rv-hint { color: #15803D; background: #ECFDF3; border: 1px solid #BBF7D0; border-radius: 10px;
  padding: 8px 10px; font-size: .82rem; font-weight: 500; line-height: 1.4; margin: 0 0 10px; }
"""


def _back():
    st.session_state.page = "Dashboard"
    st.session_state.pop("view_resume", None)
    st.session_state.pop("view_template", None)
    st.rerun()


def _pick(template):
    st.session_state.view_template = template
    st.rerun()


def _fetch_pdf(resume_id, template):
    """(file_name, bytes, error): the resume in the template as a PDF, or the reason it could not be built."""
    try:
        file_name, content = download_resume(resume_id, template, "pdf")
        return file_name, content, None
    except ApiError as e:
        return None, None, str(e)


def _page_count(pdf):
    try:
        return len(PdfReader(io.BytesIO(pdf)).pages)
    except Exception:  # noqa: BLE001 - only the toolbar's page count is lost
        return None


def _render_files(view, names, template):
    """Left pane: back, the resume's title and the template list."""
    with st.container(key="rv_files"):
        if st.button("Dashboard", icon=":material/arrow_back:", key="rv_back"):
            _back()
        html(f'<div class="r-rv-title">{_html.escape(view["title"])}</div>')
        html('<div class="r-rv-label">TEMPLATES</div>')
        html('<div class="r-rv-hint">Your resume is available in different templates. Pick one to preview it, '
             'then download it as a PDF.</div>')
        for template_id, name in names.items():
            if st.button(name, key=f"rv_tpl_{template_id}", icon=":material/description:",
                         type="primary" if template_id == template else "secondary", use_container_width=True):
                _pick(template_id)


def _render_preview(resume_id, names, template, pdf_file):
    """Right pane: template name, page count and the PDF download above the resume."""
    pdf_name, pdf, error = pdf_file
    with st.container(key="rv_preview"):
        name, pages, download = st.columns([3, 2, 2], vertical_alignment="center")
        with name:
            html(f'<div class="r-rv-title">{_html.escape(names[template])} template</div>')
        with pages:
            count = _page_count(pdf) if pdf else None
            if count:
                html(f'<span class="r-rv-pages">{count} page{"s" if count > 1 else ""}</span>')
        with download:
            if pdf:
                st.download_button("Download PDF", pdf, pdf_name, PDF_MIME, icon=":material/download:",
                                   type="primary", use_container_width=True, key=f"rv_dl_pdf_{resume_id}")
        if error:
            st.error(error)
        else:
            st.pdf(pdf, height=PANE_HEIGHT)


def render():
    view = st.session_state.get("view_resume")
    if not view:
        _back()
    css(_CSS)

    try:
        templates = list_templates()
    except ApiError as e:
        st.error(str(e))
        return
    if not templates:
        st.info("No resume templates are available yet.")
        return
    names = {t["id"]: t["name"] for t in templates}
    template = st.session_state.get("view_template")
    if template not in names:
        template = DEFAULT_TEMPLATE if DEFAULT_TEMPLATE in names else next(iter(names))

    files, preview = st.columns([1.1, 4.4], gap="medium")
    with files:
        _render_files(view, names, template)
    with preview:
        _render_preview(view["id"], names, template, _fetch_pdf(view["id"], template))
