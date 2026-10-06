from app.steps.jd import JobDescriptionExtractor
from app.steps.keywords import KeywordMatcher

extract_jd = JobDescriptionExtractor().extract
find_skills = KeywordMatcher().find


def test_skills_respect_word_boundaries_and_aliases():
    text = "Java and JavaScript, MySQL, PostgreSQL (postgres), k8s, Node.js, C++, C#, CI/CD, Spring Boot"
    assert find_skills(text) == ["java", "javascript", "mysql", "postgresql", "kubernetes", "node.js",
                                 "c++", "c#", "ci/cd", "spring boot"]


def test_go_only_matches_the_language_not_the_verb():
    assert find_skills("we go fast and go far") == []
    assert find_skills("services written in Go and Golang") == ["go"]


JD = """Senior Backend Engineer
About us
We build cloud software on AWS.
Responsibilities
- Design microservices
Requirements
- 5+ years of experience with Java and Spring Boot
- Strong knowledge of Kafka and PostgreSQL
Nice to have
- Terraform
"""


def test_extract_jd_splits_sections_and_skills():
    jd = extract_jd(JD)

    assert jd["title"] == "Senior Backend Engineer"
    assert jd["requirements"] == ["5+ years of experience with Java and Spring Boot",
                                  "Strong knowledge of Kafka and PostgreSQL"]
    assert jd["preferred"] == ["Terraform"]
    assert jd["min_years"] == 5
    assert jd["preferred_skills"] == ["terraform"]
    # skills named only in prose (AWS in "About us", microservices under Responsibilities) still count as required
    assert set(jd["required_skills"]) == {"java", "spring boot", "kafka", "postgresql", "aws", "microservices"}


def test_extract_jd_without_headings_treats_every_skill_as_required():
    jd = extract_jd("We need a Python developer who knows Docker and AWS.")

    assert jd["title"] is None  # a sentence, not a title
    assert jd["required_skills"] == ["python", "docker", "aws"]
    assert jd["preferred_skills"] == []


def test_extract_jd_reads_an_explicit_title_label():
    assert extract_jd("Job Title: Platform Engineer\nRequirements\n- Go")["title"] == "Platform Engineer"
