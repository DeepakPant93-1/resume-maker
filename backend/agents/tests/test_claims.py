from app.steps.claims import ClaimParser

parse_claims = ClaimParser().parse
merge_claims = ClaimParser().merge

DRAFT = """\
Experience
- Led migration to microservices
- Cut deploy time 40%
Summary
- Backend engineer
Needs user input
- How many engineers did you mentor?
"""


def test_parse_claims_extracts_sections_and_needs_input():
    claims, needs = parse_claims(DRAFT)

    assert [(c["section"], c["text"]) for c in claims] == [
        ("Experience", "Led migration to microservices"),
        ("Experience", "Cut deploy time 40%"),
        ("Summary", "Backend engineer"),
    ]
    assert needs == ["How many engineers did you mentor?"]


def test_merge_replaces_only_the_sections_in_the_new_draft():
    old = [{"text": "a", "section": "Experience"}, {"text": "b", "section": "Summary"}]
    new = [{"text": "c", "section": "Experience"}]

    assert merge_claims(old, new) == [{"text": "b", "section": "Summary"}, {"text": "c", "section": "Experience"}]
