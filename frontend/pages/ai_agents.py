"""AI Agents Page (Figma: ai-agents workspace, agent-chat, agent-result)"""
import copy
import html as _html
import re

import streamlit as st

from pages.job_match import KEYWORDS
from pages.my_resumes import editor_preview_html, initialize_resume_data
from styles.theme import card, css, html, page_header

AGENTS = [
    ("Resume Agent", True, "Optimizes resume layout, terminology, and key sections.",
     ["Analyze core skills", "Suggest technical synonyms", "Refine spacing density"]),
    ("ATS Agent", True, "Parses and scores content against top ATS algorithms.",
     ["Identify keyword gaps", "Check structure compatibility", "Calculate scoring index"]),
    ("Job Match Agent", True, "Compares experience against target job descriptions.",
     ["Extract job requisites", "Correlate achievements", "Highlight matches"]),
    ("Skill Gap Agent", True, "Discovers and recommends missing technical requirements.",
     ["Identify industry standards", "Suggest learning paths", "Synthesize tech keywords"]),
    ("Content Agent", False, "Refines tone of voice, professional impact, and brevity.",
     ["Polishes vocabulary", "Removes passive grammar", "Highlights active verbs"]),
    ("Review Agent", False, "Verifies grammar, credentials accuracy, and consistency.",
     ["Spell-check validation", "Date chronology audit", "Formatting review"]),
    ("Interview Agent", False, "Generates tailored mock interview questions from content.",
     ["Synthesize scenario tests", "Draft responses outline", "Formulate behavior questions"]),
    ("Career Advisor", False, "Analyzes industry trajectories and outlines pathways.",
     ["Track market demands", "Outline title progressions", "Audit salary brackets"]),
]
QUICK_ACTIONS = ["Tailor to a job", "Add metrics", "Fix grammar", "Shorten to 1 page"]

_ICON = ('<div style="width:30px;height:30px;border-radius:8px;background:#EFEBFD;color:#6C4FE0;'
         'display:flex;align-items:center;justify-content:center;font-size:0.85rem;flex-shrink:0">✦</div>')

_CSS = """
.r-agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }
.r-agent-head { display: flex; align-items: center; gap: 0.6rem; }
.st-key-open_agent button p { white-space: nowrap; }
.r-agent-name { font-weight: 600; font-size: 0.9rem; color: #111827; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.r-agent-desc { font-size: 0.8rem; color: #6B7280; margin: 0.7rem 0; min-height: 2.4rem;
                padding-bottom: 0.7rem; border-bottom: 1px solid #EEF0F4; }
.r-agent-li { font-size: 0.76rem; color: #6B7280; margin: 0.3rem 0; }
.r-bubble { padding: 0.65rem 0.85rem; border-radius: 10px; font-size: 0.85rem; margin: 0.4rem 0; max-width: 88%; line-height: 1.45; }
.r-bubble.agent { background: #F3F4F6; color: #111827; }
.r-bubble.user { background: #6C4FE0; color: #fff; margin-left: auto; }
.r-bubble .ok { color: #22A06B; }
.st-key-card_chat [data-testid="stForm"] { border: 1.5px solid #6C4FE0; border-radius: 10px; padding: 0.6rem; }
.st-key-card_chat [data-baseweb="textarea"], .st-key-card_chat [data-baseweb="input"] { border: none !important; }
.st-key-card_agentresume .rv { padding: 0.75rem 1.25rem; }
[data-testid="stMain"] .st-key-chip_agent_row button[data-testid] { border-radius: 999px !important; }
.st-key-card_chat button p { white-space: nowrap; }
"""

_FOCUS_CSS = """
section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"] { display: none !important; }
"""


def render_workspace():
    head, btn = st.columns([3, 1], vertical_alignment="center")
    with head:
        page_header("AI Agent Workspace", "Specialized autonomous agents collaborating to optimize your professional profile.")
    with btn:
        if st.button("✦ Open Resume Agent", type="primary", use_container_width=True, key="open_agent"):
            st.session_state.agent_view = "chat"
            st.rerun()

    cards = []
    for name, active, desc, tasks in AGENTS:
        status = ('<span class="r-badge">Active</span>' if active
                  else '<span class="r-badge idle">Idle</span>')
        items = "".join(f'<div class="r-agent-li">✓ {t}</div>' for t in tasks)
        cards.append(f'<div class="r-card"><div class="r-agent-head">{_ICON}'
                     f'<span class="r-agent-name">{name}</span>{status}</div>'
                     f'<div class="r-agent-desc">{desc}</div>{items}</div>')
    html(f'<div class="r-agent-grid">{"".join(cards)}</div>')


# ---------------------------------------------------------------------------
# The "brain" of the agent.
# Replace propose_changes() with a call to your LLM (e.g. Claude API) that returns
# (updated_resume, list_of_change_descriptions, set_of_highlight_keys).
# The demo below applies simple rule-based edits so the UI flow works end-to-end.
# ---------------------------------------------------------------------------

def propose_changes(prompt: str, resume: dict):
    new = copy.deepcopy(resume)
    low = prompt.lower()
    changes, highlight = [], set()
    role_m = re.search(r"for an? (.+?)(?: role| position| job|,|\.| at |$)", prompt, re.I)
    role_text = role_m.group(1).lower() if role_m else ""
    mentioned = [k for k in KEYWORDS
                 if re.search(r"(?<![\w])" + re.escape(k.lower()) + r"(?![\w])", low)
                 and k.lower() not in role_text]
    nice = lambda xs: xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

    # 1) Rewrite / tailor the summary
    if any(w in low for w in ("summary", "rewrite", "tailor")):
        role = role_m.group(1).strip() if role_m else new["profile"]["job_title"]
        ctx = re.search(r" at an? (.+?)(?: company| startup|,|\.|$)", prompt, re.I)
        old = new["profile"]["summary"]
        tail = old.split(" with ", 1)[1] if " with " in old else old
        summary = f"{role} with {tail}"
        if ctx:
            summary += f" Experienced in building {ctx.group(1).strip()} systems."
        if mentioned:
            summary += f" Focused on {nice(mentioned[:3])}."
        new["profile"]["summary"] = summary
        changes.append(f"Rewrote your summary{' for a ' + ctx.group(1).strip() + ' role' if ctx else ''}")
        highlight.add("summary")

    # 2) Move mentioned skills to the top
    if mentioned:
        sk = new["skills"]
        for cat in ("languages", "frameworks", "tools"):
            sk[cat] = [x for x in sk.get(cat, []) if x not in mentioned]
        sk["languages"] = mentioned + sk["languages"]
        changes.append(f"Moved {nice(mentioned[:3])} to the top of Skills")
        highlight.add("skills")

    # 3) Add metrics / shorten
    jobs = [j for j in new["experience"] if j.get("job_title") or j.get("company")]
    if "metric" in low or "number" in low:
        for i, job in enumerate(jobs):
            lines = [l for l in job["achievements"].splitlines() if l.strip()]
            fixed = [l if re.search(r"\d", l) else l.rstrip(".") + " (add a measurable result, e.g. 30%)" for l in lines]
            if fixed != lines:
                job["achievements"] = "\n".join(fixed)
                highlight.add(f"exp{i}")
        if any(k.startswith("exp") for k in highlight):
            changes.append("Flagged bullets that need a measurable result")
    if "shorten" in low or "1 page" in low or "one page" in low:
        for i, job in enumerate(jobs):
            lines = [l for l in job["achievements"].splitlines() if l.strip()]
            if len(lines) > 2:
                job["achievements"] = "\n".join(lines[:2])
                highlight.add(f"exp{i}")
        changes.append("Trimmed each role to its 2 strongest bullets")

    return new, changes, highlight


def _prefill(text):
    st.session_state.agent_input = text


def _back_target():
    return st.session_state.get("agent_back", "MyResumes")


def _render_bubbles():
    for role, text in st.session_state.agent_messages:
        html(f'<div class="r-bubble {role}">{text}</div>')


def render_chat():
    initialize_resume_data()
    css(_FOCUS_CSS)
    if "agent_messages" not in st.session_state:
        first = st.session_state.get("user", {}).get("name", "there").split()[0]
        st.session_state.agent_messages = [
            ("agent", f"Hi {first}! Tell me what you want to change in your resume and I will edit it for you.")
        ]
    pending = st.session_state.get("agent_pending")

    with st.container(key="topbar"):
        html('<span style="font-weight:700;color:#6C4FE0;font-size:1.05rem">ResuAI</span>')

    back_label = "← Back to editor" if _back_target() == "MyResumes" else "← Back"
    if st.button(back_label, type="tertiary", key="agent_back_btn"):
        st.session_state.page = _back_target()
        st.session_state.agent_view = "workspace"
        st.session_state.pop("agent_back", None)
        st.rerun()

    if pending:
        page_header("Review AI changes", "Your resume was updated based on your instructions.")
    else:
        page_header("AI Resume Agent", "Describe the change you want. The agent edits your resume for you.")

    left, right = st.columns([3, 2])
    with left:
        with card("agentresume"):
            if pending:
                html(editor_preview_html(pending["resume"], highlight=pending["highlight"]))
            else:
                html(editor_preview_html())

    with right:
        with card("chat"):
            html(f'<div style="display:flex;gap:0.6rem;align-items:center;padding-bottom:0.7rem;'
                 f'border-bottom:1px solid #EEF0F4;margin-bottom:0.5rem">{_ICON}'
                 f'<div><div style="font-weight:600;font-size:0.9rem">Resume Agent</div>'
                 f'<div class="r-muted"><span style="color:#22A06B">●</span> Online</div></div></div>')

            with st.container(height=300 if pending else 330, border=False):
                _render_bubbles()
                if not pending and len(st.session_state.agent_messages) == 1:
                    with st.container(key="chip_agent_row"):
                        for row in (QUICK_ACTIONS[:2], QUICK_ACTIONS[2:]):
                            for col, action in zip(st.columns(2), row):
                                with col:
                                    st.button(action, key=f"chip_{action}", on_click=_prefill, args=(action,),
                                              use_container_width=True)
            if pending:
                a, u, _ = st.columns([1.4, 0.9, 0.7])
                with a:
                    if st.button("Accept changes", type="primary", use_container_width=True, key="agent_accept"):
                        st.session_state.resume_data = pending["resume"]
                        st.session_state.agent_messages.append(("agent", '<span class="ok">✓</span> Changes applied to your resume.'))
                        st.session_state.agent_pending = None
                        st.rerun()
                with u:
                    if st.button("Undo", use_container_width=True, key="agent_undo"):
                        st.session_state.agent_messages.append(("agent", "No problem, I undid those changes."))
                        st.session_state.agent_pending = None
                        st.rerun()

            with st.form("agent_form", clear_on_submit=True, border=False):
                if pending:
                    prompt = st.text_input("Message", key="agent_input", label_visibility="collapsed",
                                           placeholder="Ask for another change…")
                else:
                    prompt = st.text_area("Message", key="agent_input", height=80, label_visibility="collapsed",
                                          placeholder="e.g. Rewrite my summary for a Senior Java Developer role "
                                                      "at a fintech company and highlight Kafka and AWS.")
                _, send = st.columns([2, 1])
                with send:
                    sent = st.form_submit_button("Send →", type="primary", use_container_width=True)

            if sent and prompt.strip():
                base = pending["resume"] if pending else st.session_state.resume_data
                st.session_state.agent_messages.append(("user", _html.escape(prompt)))
                new, changes, highlight = propose_changes(prompt, base)
                if changes:
                    items = "".join(f'<div><span class="ok">✓</span>&nbsp; {_html.escape(c)}</div>' for c in changes)
                    st.session_state.agent_messages.append((
                        "agent",
                        f'<b>Done! I made {len(changes)} change{"s" if len(changes) > 1 else ""}:</b>'
                        f'<div style="margin:0.4rem 0">{items}</div>'
                        '<div class="r-muted">Changes are highlighted in yellow on the left. '
                        'Review them, then accept or undo.</div>'))
                    st.session_state.agent_pending = {"resume": new, "highlight": highlight}
                else:
                    st.session_state.agent_messages.append((
                        "agent", "I couldn't turn that into an edit yet. Try mentioning the summary, "
                                 "skills (e.g. Kafka, AWS), metrics or shortening."))
                st.rerun()


def render():
    css(_CSS)
    if st.session_state.get("agent_view") == "chat":
        render_chat()
    else:
        render_workspace()
