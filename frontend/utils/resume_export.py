"""Turns a resume (in the editor's shape, see api_client.to_editor_data) into a downloadable PDF."""
import io
import re

PDF_MIME = "application/pdf"


def file_stem(data):
    """A safe file name (no extension) for the resume, e.g. "Suraj_Singh_Karki_Resume"."""
    name = (data.get("profile") or {}).get("full_name") or "Resume"
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") + "_Resume"


def _bullets(text):
    return [line.strip().lstrip("•-* ").strip() for line in str(text or "").splitlines() if line.strip().lstrip("•-* ")]


def _span(*parts):
    return " – ".join(p for p in parts if p)


def _sections(data):
    """The resume as plain data: (name, title, contact, [(heading, [("line"|"bullet"|"entry", text, right_text)])])."""
    p = data.get("profile") or {}
    skills = data.get("skills") or {}
    blocks = []
    if p.get("summary"):
        blocks.append(("Professional Summary", [("line", p["summary"], "")]))

    rows = []
    for job in data.get("experience") or []:
        heading = " — ".join(x for x in (job.get("job_title"), job.get("company")) if x)
        if not heading:
            continue
        end = "Present" if job.get("current") else job.get("end_date")
        rows.append(("entry", heading, _span(job.get("start_date"), end)))
        rows += [("bullet", b, "") for b in _bullets(job.get("achievements"))]
    if rows:
        blocks.append(("Experience", rows))

    rows = []
    for edu in data.get("education") or []:
        heading = " — ".join(x for x in (edu.get("degree"), edu.get("university")) if x)
        if not heading:
            continue
        rows.append(("entry", heading, _span(edu.get("start_year"), edu.get("end_year"))))
        if edu.get("grade"):
            rows.append(("line", edu["grade"], ""))
    if rows:
        blocks.append(("Education", rows))

    rows = [("line", f"{label}: {', '.join(skills[key])}", "")
            for label, key in (("Languages", "languages"), ("Frameworks", "frameworks"), ("Tools", "tools"))
            if skills.get(key)]
    if rows:
        blocks.append(("Skills", rows))

    rows = []
    for proj in data.get("projects") or []:
        if proj.get("name"):
            rows.append(("entry", proj["name"], proj.get("technologies") or ""))
            if proj.get("description"):
                rows.append(("line", proj["description"], ""))
    if rows:
        blocks.append(("Projects", rows))

    rows = [("line", " — ".join(x for x in (c.get("name"), c.get("issuer")) if x), "")
            for c in data.get("certifications") or [] if c.get("name")]
    if rows:
        blocks.append(("Certifications", rows))
    return blocks


def _header(data):
    p = data.get("profile") or {}
    contact = " · ".join(p[k] for k in ("email", "phone", "location", "linkedin") if p.get(k))
    return p.get("full_name") or "Your Name", p.get("job_title") or "", contact


def to_pdf(data):
    """The resume as the bytes of a one-column, ATS-friendly PDF (real text, no images).

    Uses the built-in Helvetica fonts, which cover Latin text and the usual punctuation (• – — ·); characters
    outside that range, such as Devanagari or emoji, cannot be drawn and show as filled boxes.
    """
    from xml.sax.saxutils import escape

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    accent = colors.HexColor("#6C4FE0")
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=9.5, leading=13)
    name_style = ParagraphStyle("name", parent=body, fontName="Helvetica-Bold", fontSize=20, leading=24)
    title_style = ParagraphStyle("title", parent=body, fontSize=11, leading=14, textColor=accent)
    contact_style = ParagraphStyle("contact", parent=body, fontSize=9, textColor=colors.HexColor("#4B5563"))
    heading_style = ParagraphStyle("heading", parent=body, fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                                   textColor=accent, spaceBefore=10)
    entry_style = ParagraphStyle("entry", parent=body, fontName="Helvetica-Bold", spaceBefore=4)
    right_style = ParagraphStyle("right", parent=body, fontSize=9, alignment=TA_RIGHT,
                                 textColor=colors.HexColor("#4B5563"))
    bullet_style = ParagraphStyle("bullet", parent=body, leftIndent=12, bulletIndent=2)

    name, title, contact = _header(data)
    story = [Paragraph(escape(name), name_style)]
    if title:
        story.append(Paragraph(escape(title), title_style))
    if contact:
        story.append(Paragraph(escape(contact), contact_style))
    for heading, rows in _sections(data):
        story += [Paragraph(heading.upper(), heading_style),
                  HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#D1D5DB"), spaceAfter=3)]
        for kind, text, right in rows:
            if kind == "entry":
                row = Table([[Paragraph(escape(text), entry_style), Paragraph(escape(right), right_style)]],
                            colWidths=[None, 55 * mm])
                row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                         ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                         ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
                story.append(row)
            elif kind == "bullet":
                story.append(Paragraph(escape(text), bullet_style, bulletText="•"))
            else:
                story.append(Paragraph(escape(text), body))
    story.append(Spacer(1, 1))

    buffer = io.BytesIO()
    SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                      bottomMargin=16 * mm, title=f"{name} - Resume", author=name).build(story)
    return buffer.getvalue()
