from app.steps.claims import ClaimParser, ClaimValidator

parse_claims = ClaimParser().parse
merge_claims = ClaimParser().merge

RESUME = {
    "profile": {"summary": "Backend engineer"},
    "experience": [{"company": "Coredge", "achievements": "• Cut deploy time 40%\n• Mentored 2 engineers"}],
    "skills": {"languages": ["Python", "Go"], "tools": []},
}


def test_resolves_nested_paths_and_indexes():
    assert ClaimValidator(RESUME).resolve("profile.summary") == "Backend engineer"
    assert ClaimValidator(RESUME).resolve("experience[0].company") == "Coredge"
    assert ClaimValidator(RESUME).resolve("skills.languages[1]") == "Go"


def test_missing_empty_or_malformed_paths_resolve_to_none():
    for ref in ("experience[5].company", "profile.nope", "skills.tools", "experience[0", "", "..x", "a b"):
        assert ClaimValidator(RESUME).resolve(ref) is None, ref


def test_validate_claims_flags_missing_and_nonexistent_refs():
    claims = [
        {"text": "Good claim", "source_ref": "profile.summary", "section": None},
        {"text": "No ref", "source_ref": None, "section": None},
        {"text": "Bad ref", "source_ref": "experience[3].achievements", "section": None},
    ]
    issues = ClaimValidator(RESUME).validate(claims)
    assert len(issues) == 2
    assert "Claim 2" in issues[0] and "no source_ref" in issues[0]
    assert "Claim 3" in issues[1] and "does not exist" in issues[1]


DRAFT = """\
Experience
- Led migration to microservices [source_ref: experience[0].achievements]
- Invented a 10x speedup
Summary
Backend engineer who ships [source_ref: profile.summary]
Needs user input
- How many engineers did you mentor?
"""


def test_parse_claims_extracts_sections_refs_and_needs_input():
    claims, needs = parse_claims(DRAFT)

    assert [(c["section"], c["source_ref"]) for c in claims] == [
        ("Experience", "experience[0].achievements"),
        ("Experience", None),  # unsourced bullet is kept so the reviewer can reject it
        ("Summary", "profile.summary"),
    ]
    assert claims[0]["text"] == "Led migration to microservices"
    assert needs == ["How many engineers did you mentor?"]


def test_merge_replaces_only_the_sections_in_the_new_draft():
    old = [{"text": "a", "section": "Experience"}, {"text": "b", "section": "Summary"}]
    new = [{"text": "c", "section": "Experience"}]

    assert merge_claims(old, new) == [{"text": "b", "section": "Summary"}, {"text": "c", "section": "Experience"}]
