"""Templates Page (Figma: templates)"""
import streamlit as st

from components.resume_preview import TEMPLATES, template_thumb
from styles.theme import card, css, html, page_header

FILTERS = ["All", "ATS-friendly", "Modern", "Simple", "Creative"]


def _use_template(name):
    st.session_state.selected_template = name
    builder = st.session_state.get("new_resume")
    if builder is not None:
        builder["template"] = name
    st.session_state.page = "CreateResume"
    st.session_state.builder_mode = "builder"
    # Coming back from the wizard's template step -> return there; otherwise start at step 1
    if not builder or not builder["personal_info"]["full_name"]:
        st.session_state.builder_step = 1
    else:
        st.session_state.builder_step = 5
    st.rerun()


def render():
    selected = st.session_state.get("selected_template", "Modern")

    head, filt = st.columns([3, 2], vertical_alignment="bottom")
    with head:
        page_header("Choose a template", "Pick a layout to start with. You can switch templates any time.")
    with filt:
        choice = st.pills("Filter", FILTERS, default="All", key="tpl_filter", label_visibility="collapsed")
    choice = choice or "All"

    shown = [t for t in TEMPLATES if choice == "All" or choice in t[4]]
    css(f".st-key-card_tpl_{selected} {{ border: 1.5px solid #6C4FE0 !important; }}")

    cols = st.columns(3)
    for i, (name, desc, accent, style, _tags) in enumerate(shown):
        with cols[i % 3]:
            with card(f"tpl_{name}"):
                ribbon = ('<span class="r-badge purple" style="position:absolute;margin:8px">Recommended</span>'
                          if name == "Modern" else "")
                html(f'<div style="position:relative">{ribbon}{template_thumb(accent, style, 170)}</div>')
                html(f'<div style="font-weight:600;font-size:0.9rem;margin-top:0.5rem">{name}</div>'
                     f'<div class="r-muted" style="margin-bottom:0.5rem">{desc}</div>')
                if st.button("Use template", key=f"use_{name}",
                             type="primary" if name == selected else "secondary",
                             use_container_width=True):
                    _use_template(name)
    if not shown:
        st.caption("No templates match this filter.")
