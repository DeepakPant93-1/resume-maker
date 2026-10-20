"""Helpers for showing an AI run's result and applying it to the editor's resume."""
import copy


def _section_kind(section):
    """Which editor section a claim's heading names: "summary", "experience", or None for anything else."""
    name = (section or "").lower()
    if "summary" in name or "profile" in name:
        return "summary"
    if "experience" in name or "work" in name:
        return "experience"
    return None


def apply_claims(resume_data, claims):
    """Write the AI's rewritten claims into a copy of the editor's resume.

    A claim carries the section heading it was written under. Summary claims replace the professional summary.
    Experience claims do not say which job they belong to, so they are added to the most recent job's bullets
    (skipping any bullet already there) rather than replacing anything. Claims for other sections (skills,
    projects...) are left out, since there is no safe place to put them.

    Returns (new_resume_data, applied_count, skipped_count). The input is not modified.
    """
    new = copy.deepcopy(resume_data)
    summary, bullets, skipped, added = [], [], 0, 0
    for claim in claims:
        kind = _section_kind(claim.get("section"))
        if kind == "summary":
            summary.append(claim["text"])
        elif kind == "experience" and new.get("experience"):
            bullets.append(claim["text"])
        else:
            skipped += 1

    if summary:
        new["profile"]["summary"] = " ".join(summary)
    if bullets:
        job = new["experience"][0]
        existing = job.get("achievements") or ""
        present = {line.lstrip("•-* ").strip() for line in existing.splitlines()}
        fresh = [text for text in bullets if text.strip() not in present]
        job["achievements"] = "\n".join([existing] * bool(existing) + ["• " + text for text in fresh])
        added = len(fresh)
        skipped += len(bullets) - added
    return new, len(summary) + added, skipped
