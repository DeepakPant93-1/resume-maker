from app.steps.ats import ats_score, resume_bullets
from app.steps.jd import extract_jd

RESUME = {
    "profile": {"full_name": "A", "email": "a@x.io", "phone": "+91 99999 99999", "job_title": "Backend Engineer",
                "summary": "Backend engineer with Python experience."},
    "experience": [{"job_title": "Engineer", "company": "Acme",
                    "achievements": "• Cut deploy time by 40% using Docker\n• Mentored junior engineers"}],
    "education": [{"degree": "B.Tech"}],
    "skills": {"languages": ["Python"], "frameworks": [], "tools": ["Docker"]},
    "projects": [], "certifications": [],
}


def test_without_a_job_the_score_covers_structure_only():
    report = ats_score(RESUME)

    assert report["against_job"] is False
    assert set(report["components"]) == {"completeness", "impact", "readability"}
    assert sum(c["max"] for c in report["components"].values()) == 100
    assert report["components"]["impact"]["with_numbers"] == 1  # one of two bullets has a number
    assert any("1 of 2 bullets" in s for s in report["suggestions"])


def test_with_a_job_keywords_dominate_and_missing_ones_are_listed():
    jd = extract_jd("Requirements\n- Python, Docker, Kafka and Terraform")

    report = ats_score(RESUME, jd)
    keywords = report["components"]["keywords"]

    assert report["against_job"] is True
    assert keywords["matched"] == ["python", "docker"] and keywords["missing"] == ["kafka", "terraform"]
    assert keywords["points"] == 25.0  # half of the 50 keyword points
    assert any("kafka" in s and "truthfully" in s for s in report["suggestions"])


def test_draft_text_counts_towards_keyword_match():
    jd = extract_jd("Requirements\n- Python and Kafka")

    base = ats_score(RESUME, jd)["components"]["keywords"]["points"]
    with_draft = ats_score(RESUME, jd, extra_text="Built Kafka consumers")["components"]["keywords"]["points"]

    assert (base, with_draft) == (25.0, 50.0)


def test_incomplete_resume_loses_completeness_points():
    report = ats_score({"profile": {"full_name": "A"}})

    assert report["components"]["completeness"]["missing"] == ["email", "phone", "summary", "experience",
                                                                "education", "skills"]
    assert report["components"]["impact"]["points"] == 0.0
    assert report["score"] < 40


def test_long_summary_and_bullets_hurt_readability():
    wordy = " ".join(["word"] * 130)
    resume = {**RESUME, "profile": {**RESUME["profile"], "summary": wordy},
              "experience": [{"achievements": "• " + " ".join(["x"] * 40)}]}

    report = ats_score(resume)

    assert report["components"]["readability"]["points"] == 0
    assert resume_bullets(resume)[0].startswith("x")
