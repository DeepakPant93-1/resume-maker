"""Helpers for showing an AI run's result and applying it to the editor's resume."""
import copy
import re

_EXPERIENCE_REF = re.compile(r"experience\[(\d+)\]\.achievements")


def apply_claims(resume_data, claims):
    """Write the AI's rewritten claims into a copy of the editor's resume.

    A claim points at the original text it rewrites through its `source_ref`. Claims for `profile.summary`
    replace the summary; claims for `experience[i].achievements` replace that job's bullets. Claims pointing
    anywhere else (skills, projects...) are left out, since there is no safe place to put them.

    Returns (new_resume_data, applied_count, skipped_count). The input is not modified.
    """
    new = copy.deepcopy(resume_data)
    summary, bullets, skipped = [], {}, 0
    for claim in claims:
        ref = (claim.get("source_ref") or "").replace(" ", "")
        match = _EXPERIENCE_REF.fullmatch(ref)
        if ref == "profile.summary":
            summary.append(claim["text"])
        elif match and int(match.group(1)) < len(new["experience"]):
            bullets.setdefault(int(match.group(1)), []).append(claim["text"])
        else:
            skipped += 1

    if summary:
        new["profile"]["summary"] = " ".join(summary)
    for index, texts in bullets.items():
        new["experience"][index]["achievements"] = "\n".join("• " + text for text in texts)
    applied = len(summary) + sum(len(texts) for texts in bullets.values())
    return new, applied, skipped
