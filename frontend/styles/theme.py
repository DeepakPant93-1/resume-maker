"""
ResuAI theme - matches the Figma design
(white sidebar, light grey canvas, flat purple accents, Inter font)
"""
from typing import Optional

import streamlit as st

COLORS = {
    "primary": "#6C4FE0",
    "primary_hover": "#5B3FD1",
    "primary_soft": "#EFEBFD",
    "bg": "#F5F6FA",
    "surface": "#FFFFFF",
    "border": "#E6E8EF",
    "text": "#111827",
    "muted": "#6B7280",
    "success": "#22A06B",
    "success_soft": "#E7F6EE",
}

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ---------- Base ---------- */
html, body, .stApp, p, li, label, input, textarea, button,
h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp { background: #F5F6FA; color: #111827; }

/* Hide Streamlit chrome (Deploy, menu, auto page list, footer) */
#MainMenu, footer,
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebarNav"], [data-testid="stAppDeployButton"] {
    display: none !important;
}
/* Keep the header (it holds the "open sidebar" button) but make it invisible */
header[data-testid="stHeader"] {
    background: transparent !important; height: 0 !important; min-height: 0 !important;
    visibility: hidden;
}
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important; position: fixed !important; top: 0.75rem; left: 0.75rem;
    z-index: 999990; background: #FFFFFF; border: 1px solid #E6E8EF; border-radius: 8px;
}

/* <style>-only blocks take no space (removes stray gaps) */
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style) { display: none !important; }

/* Main content area */
.block-container, [data-testid="stMainBlockContainer"] {
    padding: 0 2rem 2rem 2rem !important;
    max-width: none !important;
}

h1 { font-size: 1.75rem !important; font-weight: 700 !important; letter-spacing: -0.02em; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; }
hr { border-color: #E6E8EF !important; margin: 1rem 0 !important; }

/* ---------- Top bar ---------- */
.st-key-topbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E6E8EF;
    margin: 0 -2rem 1.5rem -2rem;
    padding: 0.7rem 2rem;
}
.st-key-topbar [data-baseweb="input"] {
    border: 1px solid #E6E8EF !important; background: #FFFFFF !important; max-width: 340px;
}
.st-key-topbar input { padding: 0.45rem 0.75rem !important; font-size: 0.8rem !important; }
[data-testid="stSidebarHeader"] { position: absolute; top: 0.6rem; right: 0.6rem; height: auto !important; padding: 0 !important; z-index: 5; }
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.r-nav-label) { margin-bottom: 0.9rem; }
.r-user { display: flex; align-items: center; justify-content: flex-end; gap: 0.6rem; }
.r-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: #EFEBFD; color: #6C4FE0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 600;
}
.r-user-name { font-size: 0.85rem; font-weight: 600; line-height: 1.1; color: #111827; }
.r-user-role { font-size: 0.72rem; color: #6B7280; }

/* ---------- Sidebar ---------- */
/* Sidebar is always open (Figma has no collapse control) */
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] { display: none !important; }
[data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }

section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E6E8EF;
    width: 240px !important; min-width: 240px !important;
}
[data-testid="stSidebarUserContent"] { padding: 1.25rem 0.9rem !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.2rem !important; }

.r-brand {
    display: flex; align-items: center; gap: 0.45rem;
    font-size: 1.15rem; font-weight: 700; color: #6C4FE0;
    padding: 0 0.1rem 1.1rem 0.1rem;
}
.r-brand-dot {
    width: 14px; height: 14px; border-radius: 50%;
    background: #6C4FE0; box-shadow: inset 0 0 0 3px #B9A9F5;
}
.r-nav-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em;
    color: #6B7280; padding: 0 0.1rem;
}

/* Nav items: plain text rows, not buttons */
[data-testid="stSidebar"] .stButton button {
    justify-content: flex-start !important;
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    color: #4B5563 !important;
    font-weight: 500; font-size: 0.875rem;
    min-height: 36px; padding: 0.4rem 0.7rem !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton button > div,
[data-testid="stSidebar"] .stButton button p {
    justify-content: flex-start !important; text-align: left !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] .stButton button:hover { background: #F3F4F6 !important; color: #111827 !important; }
[data-testid="stSidebar"] .stButton button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: #EFEBFD !important; color: #6C4FE0 !important; font-weight: 600 !important;
}

/* ---------- Main buttons ---------- */
[data-testid="stMain"] .stButton button,
[data-testid="stMain"] .stFormSubmitButton button,
[data-testid="stMain"] .stDownloadButton button {
    border-radius: 8px !important;
    font-weight: 600; font-size: 0.85rem;
    box-shadow: none !important;
    min-height: 38px;
}
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[data-testid="stBaseButton-primary"] {
    background: #6C4FE0 !important; border: 1px solid #6C4FE0 !important; color: #FFFFFF !important;
}
[data-testid="stMain"] button[kind="primary"]:hover,
[data-testid="stMain"] button[data-testid="stBaseButton-primary"]:hover {
    background: #5B3FD1 !important; border-color: #5B3FD1 !important;
}
[data-testid="stMain"] button[kind="secondary"],
[data-testid="stMain"] button[data-testid="stBaseButton-secondary"] {
    background: #FFFFFF !important; border: 1px solid #6C4FE0 !important; color: #6C4FE0 !important;
}
[data-testid="stMain"] button[kind="secondary"]:hover,
[data-testid="stMain"] button[data-testid="stBaseButton-secondary"]:hover {
    background: #EFEBFD !important;
}

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    border-color: #E6E8EF !important; border-radius: 8px !important;
}

/* ---------- Cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    border-radius: 12px;
}
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"][style*="border"],
[data-testid="stMain"] .stVerticalBlock[class*="st-key-card"] {
    background: #FFFFFF; border-color: #E6E8EF !important; border-radius: 12px !important;
}
.r-card {
    background: #FFFFFF; border: 1px solid #E6E8EF; border-radius: 12px;
    padding: 1.1rem 1.25rem;
}
.r-page-title { padding: 0 !important; font-size: 1.75rem; font-weight: 700; color: #111827; letter-spacing: -0.02em; margin: 0; }
.r-page-sub { font-size: 0.875rem; color: #6B7280; margin: 0.25rem 0 1.5rem 0; }
.r-stat-label { font-size: 0.8rem; color: #6B7280; margin-bottom: 0.35rem; }
.r-stat-value { font-size: 1.6rem; font-weight: 700; color: #111827; line-height: 1.1; }
.r-hero {
    background: #EFEBFD; border-radius: 12px; padding: 1.4rem 1.5rem;
}
.r-hero-title { font-size: 1.1rem; font-weight: 700; color: #111827; margin: 0; }
.r-hero-sub { font-size: 0.85rem; color: #6B7280; margin: 0.3rem 0 0 0; }
.r-badge {
    display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 600;
    background: #E7F6EE; color: #22A06B;
}
.r-badge.purple { background: #6C4FE0; color: #FFFFFF; }
.r-muted { color: #6B7280; font-size: 0.8rem; }
.r-badge.idle { background: #F3F4F6; color: #6B7280; }
.r-badge.soft { background: #EFEBFD; color: #6C4FE0; }
.r-badge.grey { background: #F3F4F6; color: #374151; }
.r-card-title { font-size: 1rem; font-weight: 600; color: #111827; margin: 0 0 0.75rem; }
.r-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em; color: #6B7280; text-transform: uppercase; }

/* Top bar must stretch across the gutters (fixed-width element + negative margins) */
.st-key-topbar { width: calc(100% + 4rem) !important; max-width: none !important; }

/* White cards: any st.container(key="card_...") */
[data-testid="stMain"] [class*="st-key-card_"] {
    background: #FFFFFF; border: 1px solid #E6E8EF; border-radius: 12px;
    padding: 1.1rem 1.25rem;
}

/* Tertiary buttons = plain text links ("← Back", "Browse all templates") */
[data-testid="stMain"] button[data-testid="stBaseButton-tertiary"],
[data-testid="stMain"] button[kind="tertiary"] {
    background: transparent !important; border: none !important; color: #6B7280 !important;
    padding: 0 !important; min-height: 0 !important; font-weight: 500 !important;
}
[data-testid="stMain"] button[data-testid="stBaseButton-tertiary"]:hover { color: #6C4FE0 !important; }

/* Pill-shaped chip buttons: st.button(..., key="chip_...") */
[class*="st-key-chip_"] button {
    border-radius: 999px !important; font-weight: 500 !important;
    font-size: 0.78rem !important; min-height: 30px !important; padding: 0.2rem 0.8rem !important;
}
[class*="st-key-chip_"] button p { font-size: 0.78rem !important; white-space: nowrap; }

/* Resume preview (shared by builder, editor and agent) */
.rv { background: #FFFFFF; font-size: 0.8rem; color: #374151; line-height: 1.5; }
.rv-name { font-size: 1.35rem; font-weight: 700; color: #111827; }
.rv-title { color: #6C4FE0; font-size: 0.85rem; margin-top: 0.1rem; }
.rv-contact { color: #6B7280; font-size: 0.72rem; margin: 0.25rem 0 0.6rem; padding-bottom: 0.6rem; border-bottom: 1px solid #E6E8EF; }
.rv-h { font-size: 0.66rem; font-weight: 600; letter-spacing: 0.06em; color: #9CA3AF; text-transform: uppercase; margin: 0.8rem 0 0.3rem; }
.rv-row { display: flex; justify-content: space-between; gap: 0.5rem; color: #111827; margin-top: 0.3rem; }
.rv-row span { color: #6B7280; font-size: 0.72rem; white-space: nowrap; }
.rv-li { color: #374151; }
.rv-hl { background: #FEF6D8; margin: 0.1rem -0.5rem; padding: 0.25rem 0.5rem; border-radius: 4px; }
.rv-upd { background: #E8A317; color: #fff; border-radius: 999px; padding: 0.05rem 0.5rem; font-size: 0.62rem; letter-spacing: 0; text-transform: none; }
.rv-ph { height: 7px; background: #EEF0F4; border-radius: 4px; margin: 0.35rem 0; }
"""


def apply_theme():
    """Inject global CSS. Call once, right after st.set_page_config()."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


# ---------- Small HTML helpers (keep HTML on one line so Markdown never shows it as code) ----------

def html(markup: str):
    """Render raw HTML safely. Strips indentation so it is never shown as a code block."""
    cleaned = "".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    sub = f'<p class="r-page-sub">{subtitle}</p>' if subtitle else ""
    html(f'<h1 class="r-page-title">{title}</h1>{sub}')


def stat_card(label: str, value, color: Optional[str] = None):
    style = f' style="color:{color}"' if color else ""
    html(
        f'<div class="r-card"><div class="r-stat-label">{label}</div>'
        f'<div class="r-stat-value"{style}>{value}</div></div>'
    )


def badge(text: str, variant: str = "") -> str:
    """Return badge HTML to embed inside other markup."""
    return f'<span class="r-badge {variant}">{text}</span>'


def card(name: str):
    """White bordered card. Use as: `with card("profile"): ...`"""
    return st.container(key=f"card_{name}")


def css(rules: str):
    """Inject page-specific CSS."""
    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)


def donut(score: int, color: str = "#22A06B", size: int = 96, caption: str = "") -> str:
    """Circular score ring as inline SVG (returns HTML string)."""
    r, c = 40, 251.33
    filled = c * max(0, min(score, 100)) / 100
    cap = f'<text x="50" y="64" text-anchor="middle" font-size="9" fill="#6B7280">{caption}</text>' if caption else ""
    y = 52 if caption else 56
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="#EEF0F4" stroke-width="9"/>'
        f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" '
        f'stroke-dasharray="{filled:.1f} {c}" transform="rotate(-90 50 50)"/>'
        f'<text x="50" y="{y}" text-anchor="middle" font-size="20" font-weight="700" fill="#111827">{score}{"%" if caption else ""}</text>'
        f'{cap}</svg>'
    )
