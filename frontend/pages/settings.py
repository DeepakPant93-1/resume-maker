"""Settings Page (Figma: settings + upgrade-plan)"""
import streamlit as st

from styles.theme import card, css, html, page_header

PREFERENCES = [
    ("AI writing style", "pref_style", ["Professional", "Casual", "Technical"]),
    ("Default template", "pref_template", ["Modern Pro", "Classic", "Minimal"]),
    ("Email notifications", "pref_email", ["Enabled", "Disabled"]),
    ("Auto-save frequency", "pref_autosave", ["Real-time", "Every 5 minutes", "Manual"]),
]

_CSS = """
.st-key-card_pro { background: linear-gradient(135deg, #6C4FE0 0%, #4B3BC9 100%) !important; border: none !important; color: #fff; }
[data-testid="stMain"] .st-key-card_pro button[data-testid] { background: transparent !important; color: #fff !important; border: 1px solid #ffffff66 !important; }
[data-testid="stMain"] .st-key-card_pro button[data-testid]:hover { background: #ffffff1a !important; }
.r-avatar-lg { width: 64px; height: 64px; border-radius: 50%; background: #EFEBFD; color: #6C4FE0;
               display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2rem; }
.r-plan { border: 1px solid #E6E8EF; border-radius: 12px; padding: 1.2rem; height: 100%; }
.r-plan.pro { background: #6C4FE0; color: #fff; border: none; }
.r-plan li { list-style: none; margin: 0.45rem 0; font-size: 0.85rem; }
.st-key-card_prefs [data-testid="stHorizontalBlock"] { border-bottom: 1px solid #EEF0F4; padding-bottom: 0.35rem; }
"""


def _plan_html(name, tagline, price, suffix, features, pro=False):
    items = "".join(f"<li>✓&nbsp; {f}</li>" for f in features)
    tag = '<span class="r-badge" style="float:right;background:#ffffff26;color:#fff">MOST POPULAR</span>' if pro else ""
    sub_color = "#E4DEFF" if pro else "#6B7280"
    return (f'<div class="r-plan {"pro" if pro else ""}">{tag}<div style="font-weight:600">{name}</div>'
            f'<div style="font-size:0.8rem;color:{sub_color}">{tagline}</div>'
            f'<div style="margin:0.9rem 0"><span style="font-size:1.8rem;font-weight:700">{price}</span>'
            f'<span style="font-size:0.8rem;color:{sub_color}"> {suffix}</span></div>'
            f'<ul style="padding:0">{items}</ul></div>')


@st.dialog("Upgrade to ResuAI Pro", width="large")
def upgrade_dialog():
    st.caption("Get unlimited AI edits, ATS audits and tailored cover letters.")
    free, pro = st.columns(2)
    with free:
        html(_plan_html("Free", "For getting started", "$0", "/ month",
                        ["3 resumes", "50 AI credits / month", "Basic ATS check", "2 templates"]))
        st.button("Current plan", disabled=True, use_container_width=True, key="plan_free")
    with pro:
        html(_plan_html("Pro", "For active job seekers", "$12", "/ month, billed annually",
                        ["Unlimited resumes", "Unlimited AI edits", "Full ATS audit + keyword fixes",
                         "All templates + cover letters"], pro=True))
        if st.button("Upgrade now", type="primary", use_container_width=True, key="plan_pro"):
            st.session_state.plan = "pro"
            st.rerun()
    st.caption("Cancel anytime · 7-day money-back guarantee")


def render():
    css(_CSS)
    user = st.session_state.user
    user.setdefault("location", "Noida, India")
    page_header("Settings & Profile", "Configure resume defaults, optimization engines, and manage billing tier.")

    # ---- Profile ----
    with card("profile"):
        initials = "".join(p[0] for p in user["name"].split()[:2]).upper()
        a, info, btn = st.columns([1, 7, 2], vertical_alignment="center")
        with a:
            html(f'<div class="r-avatar-lg">{initials}</div>')
        with info:
            html(f'<div style="font-weight:600;font-size:1.1rem">{user["name"]}</div>'
                 f'<div class="r-muted">{user["role"]} • {user["location"]}</div>')
        with btn:
            if st.button("Edit Profile", use_container_width=True, key="edit_profile"):
                st.session_state.editing_profile = not st.session_state.get("editing_profile", False)
                st.rerun()
        if st.session_state.get("editing_profile"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Name", user["name"])
            role = c2.text_input("Role", user["role"])
            loc = c3.text_input("Location", user["location"])
            if st.button("Save profile", type="primary", key="save_profile"):
                user.update(name=name, role=role, location=loc)
                st.session_state.editing_profile = False
                st.rerun()

    prefs, pro = st.columns(2)
    with prefs:
        with card("prefs"):
            html('<div class="r-card-title">Preferences</div>')
            for label, key, options in PREFERENCES:
                l, v = st.columns([3, 2], vertical_alignment="center")
                with l:
                    html(f'<div style="font-size:0.85rem;font-weight:500">{label}</div>')
                with v:
                    st.selectbox(label, options, key=key, label_visibility="collapsed")

    with pro:
        with card("pro"):
            is_pro = st.session_state.get("plan") == "pro"
            html('<span class="r-badge" style="background:#ffffff26;color:#fff">'
                 f'{"CURRENT PLAN" if is_pro else "PRO ACCOUNT"}</span>'
                 '<div style="font-size:1.25rem;font-weight:700;margin:0.6rem 0 0.3rem">ResuAI Pro</div>'
                 '<div style="font-size:0.82rem;color:#E4DEFF;padding-bottom:1rem;border-bottom:1px solid #ffffff33">'
                 'Unlock unlimited AI-assisted improvements, direct ATS audits, and custom tailored cover letters.</div>'
                 '<div style="margin:1rem 0"><span style="font-size:1.8rem;font-weight:700">$12</span>'
                 '<span style="font-size:0.8rem;color:#E4DEFF"> / month, billed annually</span></div>')
            if is_pro:
                st.button("You're on Pro ✓", disabled=True, use_container_width=True, key="pro_done")
            elif st.button("Upgrade Plan", use_container_width=True, key="upgrade_btn"):
                upgrade_dialog()
