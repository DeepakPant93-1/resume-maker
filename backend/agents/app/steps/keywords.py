"""Skill/keyword vocabulary shared by JD extraction and ATS scoring.

Matching is dictionary-based, not an LLM: a skill is only recognised if it is listed here (canonical
name plus aliases), so extend `SKILLS` when a technology you care about is missed.
"""
import re

# canonical name -> aliases (matching is case-insensitive unless the alias is in _CASE_SENSITIVE)
SKILLS: dict[str, tuple[str, ...]] = {
    # languages
    "python": (), "java": (), "javascript": ("js",), "typescript": ("ts",), "go": ("golang", "Go"),
    "rust": (), "c++": (), "c#": (), "kotlin": (), "scala": (), "ruby": (), "php": (), "swift": (),
    "sql": (), "bash": ("shell scripting",), "html": (), "css": (),
    # frameworks and libraries
    "spring boot": ("springboot",), "spring": ("spring framework", "spring mvc", "spring data"),
    "django": (), "flask": (), "fastapi": (), "react": ("reactjs", "react.js"), "angular": (),
    "vue": ("vue.js", "vuejs"), "node.js": ("nodejs",), "express": ("express.js",), ".net": ("dotnet",),
    "hibernate": (), "jpa": (), "langchain": (), "langgraph": (), "streamlit": (), "pytorch": (),
    "tensorflow": (), "pandas": (), "numpy": (),
    # cloud and infrastructure
    "aws": ("amazon web services",), "azure": (), "gcp": ("google cloud",), "docker": (),
    "kubernetes": ("k8s",), "terraform": (), "ansible": (), "helm": (), "jenkins": (),
    "github actions": (), "gitlab ci": (), "ci/cd": ("cicd", "ci cd"), "linux": (), "nginx": (),
    "openstack": (),
    # data
    "postgresql": ("postgres",), "mysql": (), "mongodb": ("mongo",), "redis": (), "kafka": (),
    "rabbitmq": (), "elasticsearch": (), "cassandra": (), "dynamodb": (), "snowflake": (),
    "spark": ("pyspark",), "airflow": (), "sqlite": (),
    # practices and concepts
    "microservices": ("microservice",), "rest api": ("rest apis", "restful", "restful api", "restful apis"),
    "graphql": (), "grpc": (), "agile": (), "scrum": (), "tdd": ("test-driven development",),
    "machine learning": ("ml",), "llm": ("llms", "large language models"), "nlp": (), "devops": (),
    "system design": (), "oauth": ("oauth2",), "jwt": (), "git": (), "jira": (), "prometheus": (),
    "grafana": (), "selenium": (), "junit": (), "pytest": (), "maven": (), "gradle": (),
}


class KeywordMatcher:
    """Finds the skills from a vocabulary in free text. Compiles its patterns once, then `find` is cheap."""

    # Short words that are also ordinary English: only match with this exact capitalisation.
    CASE_SENSITIVE = {"Go"}
    # Canonical names that are also ordinary words: matched only through their aliases.
    ALIAS_ONLY = {"go", "spring"}  # "spring" alone would also match inside "Spring Boot"

    def __init__(self, skills: dict[str, tuple[str, ...]] = SKILLS) -> None:
        self._patterns: dict[str, list[re.Pattern[str]]] = {
            canonical: [self._compile(name) for name in (aliases if canonical in self.ALIAS_ONLY else (canonical, *aliases))]
            for canonical, aliases in skills.items()
        }

    @classmethod
    def _compile(cls, alias: str) -> re.Pattern[str]:
        # Not glued to other word characters, so "java" does not match inside "javascript" or "mysql" inside "sql".
        pattern = r"(?<![\w+#.])" + re.escape(alias) + r"(?![\w+#])"
        return re.compile(pattern, 0 if alias in cls.CASE_SENSITIVE else re.IGNORECASE)

    def find(self, text: str) -> list[str]:
        """Canonical skills mentioned in `text`, in order of first appearance."""
        hits: list[tuple[int, str]] = []
        for canonical, patterns in self._patterns.items():
            positions = [m.start() for p in patterns if (m := p.search(text))]
            if positions:
                hits.append((min(positions), canonical))
        return [canonical for _, canonical in sorted(hits)]
