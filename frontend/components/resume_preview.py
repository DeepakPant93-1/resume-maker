"""
Shared resume rendering: live preview HTML and small template thumbnails.
"""
import html as _html


def _e(value) -> str:
    return _html.escape(str(value or ""))


def _placeholder(lines: int = 3) -> str:
    widths = [92, 80, 86, 70, 60]
    return "".join(f'<div class="rv-ph" style="width:{widths[i % 5]}%"></div>' for i in range(lines))


def resume_html(profile: dict, experience=None, education=None, skills=None,
                extras=None, show_placeholders: bool = False, highlight=None) -> str:
    """
    profile:    full_name, job_title, email, phone, location, linkedin, summary
    experience: [{job_title, company, start_date, end_date, current, achievements}]
    education:  [{degree, university, start_year, end_year, grade}]
    skills:     list[str]
    extras:     list of (heading, text) rows appended at the end
    highlight:  set of parts changed by the AI -> shown in yellow: "summary", "skills", "exp0", "exp1", ...
    """
    hl = highlight or set()

    def mark(key, inner):
        return f'<div class="rv-hl">{inner}</div>' if key in hl else inner

    experience = [j for j in (experience or []) if j.get("job_title") or j.get("company")]
    education = [e for e in (education or []) if e.get("degree") or e.get("university")]
    skills = [s for s in (skills or []) if s]

    contact = " · ".join(
        _e(profile.get(k)) for k in ("email", "phone", "location", "linkedin") if profile.get(k)
    )
    out = [
        f'<div class="rv-name">{_e(profile.get("full_name")) or "Your Name"}</div>',
        f'<div class="rv-title">{_e(profile.get("job_title"))}</div>',
        f'<div class="rv-contact">{contact}</div>',
    ]

    if "summary" in hl:
        out.append('<div class="rv-h" style="display:flex;justify-content:space-between">'
                   'Professional Summary<span class="rv-upd">Updated</span></div>')
    else:
        out.append('<div class="rv-h">Professional Summary</div>')
    if profile.get("summary"):
        out.append(mark("summary", f'<div>{_e(profile["summary"])}</div>'))
    elif show_placeholders:
        out.append(_placeholder(2))

    out.append('<div class="rv-h">Experience</div>')
    for idx, job in enumerate(experience):
        end = "Present" if job.get("current") else job.get("end_date")
        dates = " – ".join(_e(d) for d in (job.get("start_date"), end) if d)
        title = _e(job.get("job_title"))
        if job.get("company"):
            title += f' — {_e(job["company"])}'
        out.append(f'<div class="rv-row"><b>{title}</b><span>{dates}</span></div>')
        bullets = ""
        for line in str(job.get("achievements", "")).splitlines():
            line = line.strip().lstrip("•-* ").strip()
            if line:
                bullets += f'<div class="rv-li">• {_e(line)}</div>'
        out.append(mark(f"exp{idx}", bullets))
    if not experience and show_placeholders:
        out.append(_placeholder(5))

    out.append('<div class="rv-h">Education</div>')
    for edu in education:
        title = _e(edu.get("degree"))
        if edu.get("university"):
            title += f' — {_e(edu["university"])}'
        years = " – ".join(_e(y) for y in (edu.get("start_year"), edu.get("end_year")) if y)
        out.append(f'<div class="rv-row"><b>{title}</b><span>{years}</span></div>')
        if edu.get("grade"):
            out.append(f'<div class="rv-li">{_e(edu["grade"])}</div>')
    if not education and show_placeholders:
        out.append(_placeholder(2))

    out.append('<div class="rv-h">Skills</div>')
    if skills:
        out.append(mark("skills", f'<div>{" · ".join(_e(s) for s in skills)}</div>'))
    elif show_placeholders:
        out.append(_placeholder(2))

    for heading, text in extras or []:
        if text:
            out.append(f'<div class="rv-h">{_e(heading)}</div><div>{_e(text)}</div>')

    return '<div class="rv">' + "".join(out) + "</div>"


# (name, description, accent colour, header style, tags)
TEMPLATES = [
    ("Modern", "ATS-friendly · 1 page", "#6C4FE0", "bar", ["ATS-friendly", "Modern"]),
    ("Classic", "Timeless serif layout", "#111827", "bar", ["ATS-friendly", "Simple"]),
    ("Minimal", "Clean, lots of white space", "#6B7280", "bar", ["Simple", "Modern"]),
    ("Creative", "Bold header for design roles", "#C2185B", "block", ["Creative"]),
    ("Executive", "Two pages · leadership focus", "#2F6F5E", "bar", ["ATS-friendly"]),
    ("Tech", "Skills-first for engineers", "#3B6FE0", "bar", ["ATS-friendly", "Modern"]),
]


def template_thumb(accent: str, style: str = "bar", height: int = 150) -> str:
    """Tiny paper mock-up of a template."""
    lines = "".join(
        f'<div style="height:4px;background:#E5E7EB;border-radius:2px;margin:6px 0;width:{w}%"></div>'
        for w in (100, 92, 100, 84, 96, 70, 100, 88)
    )
    if style == "block":
        head = (f'<div style="background:{accent};margin:-10px -12px 8px;padding:10px 12px">'
                f'<div style="height:6px;width:60%;background:#fff;border-radius:2px"></div>'
                f'<div style="height:4px;width:40%;background:#ffffffaa;border-radius:2px;margin-top:5px"></div></div>')
    else:
        head = (f'<div style="height:3px;background:{accent};margin:-10px -12px 8px"></div>'
                f'<div style="height:6px;width:55%;background:{accent};border-radius:2px"></div>'
                f'<div style="height:4px;width:35%;background:#9CA3AF;border-radius:2px;margin-top:5px"></div>')
    return (
        f'<div style="background:#F5F6FA;border-radius:8px;height:{height}px;display:flex;'
        f'justify-content:center;align-items:flex-end;overflow:hidden;padding-top:12px">'
        f'<div style="background:#fff;width:48%;height:92%;padding:10px 12px;box-shadow:0 1px 3px #0000000f">'
        f'{head}<div style="margin-top:10px">{lines}</div></div></div>'
    )
