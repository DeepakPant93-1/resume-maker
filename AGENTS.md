# AGENTS.md

This file is the entrypoint for any AI agent (Claude, Copilot, or otherwise) working in this repository. Read it before making changes.

## What this project is

<<<<<<< Updated upstream
**Resume Maker (ResuAI)** is an AI-powered resume tailoring and optimization platform. Users provide an existing resume and a target job description; the app analyzes the gap between them and interactively rewrites the resume (via chat) to better match the role, then exports it as PDF/DOCX/Markdown.
=======
**Resume Maker (ResuAI)** is an AI-powered resume tailoring and optimization platform. Users upload or build a resume and give a target job description. The app analyzes the gap between them, rewrites the resume to match the role better (asking the user for missing facts along the way), scores it for ATS, and exports it as a PDF.
>>>>>>> Stashed changes

Full product context (problem statement, features, user journey) lives in [product/README.md](product/README.md). Individual feature specs live in [product/features/](product/features/) (e.g. `RM-01.md`).

## Repository layout

| Path | Purpose |
|---|---|
| [frontend/](frontend/) | The application UI. Built with **Streamlit** (Python). Currently the only implemented layer — see below. |
| [backend/](backend/) | Backend services. Contains two folders: [backend/resumemaker/](backend/resumemaker/) (Java Spring Boot API, scaffold only) and [backend/agents/](backend/agents/) (Python FastAPI + LangGraph agent service, in progress). Do not assume backend endpoints exist yet. |
| [doc/](doc/) | Technical/architecture documentation (structure notes, UI walkthroughs, prototype docs). |
| [product/](product/) | Product requirements: vision, problem statement, features, user journeys. Start here to understand *why* before changing *what*. |
| [.github/agents/](.github/agents/) | AI agent definitions/personas for this repo. |
| [.github/instructions/](.github/instructions/) | Scoped instructions for AI agents (e.g. per-directory or per-task rules). |
| [.github/skills/](.github/skills/) | Reusable AI agent skills for this repo. |
| [.github/prompts/](.github/prompts/) | Saved/reusable prompts for AI agents. |


## Frontend

<<<<<<< Updated upstream
- Framework: **Streamlit**, Python 3.9.
- Entry point: [frontend/app.py](frontend/app.py) → orchestrator [frontend/main.py](frontend/main.py).
- Structure: `pages/` (one module per screen: dashboard, create_resume, my_resumes, job_match, templates, ai_agents, applications, settings), `components/` (reusable UI pieces), `styles/theme.py` (all CSS/theming), `utils/` (helpers), `assets/` (images/logos).
=======
- Framework: **Streamlit**, Python 3.12+ (the Docker image uses 3.13).
- Entry point: [frontend/app.py](frontend/app.py) → orchestrator [frontend/main.py](frontend/main.py) (sidebar, routing via `PAGES`, login restore).
- Structure: `pages/` (one module per screen: dashboard, create_resume, my_resumes, job_match, templates, ai_agents, applications, settings, plus `login.py` and `ai_run.py` which are not sidebar pages), `components/` (reusable UI pieces), `styles/theme.py` (all CSS/theming), `utils/` (helpers), `assets/` (images/logos).
- Backend access: all HTTP calls go through [frontend/utils/api_client.py](frontend/utils/api_client.py). The base URL comes from `RESUMEMAKER_API_URL` (default `http://localhost:8080`).
- Auth: [frontend/utils/auth.py](frontend/utils/auth.py) keeps the JWT in `session_state` and in a cookie, so a page refresh stays logged in.
- Export: the dashboard's **View** button opens [pages/resume_view.py](frontend/pages/resume_view.py) (`ResumeView`, full screen, not in the sidebar), templates on the left (`GET /api/templates`, Classic first); clicking one shows the resume in it as a PDF on the right (`st.pdf`, needs the `streamlit[pdf]` extra) with a Download PDF button (`GET /api/resumes/{id}/download`). The backend builds the PDF; the frontend only shows it. The UI offers PDF only; the API still supports `format=tex`. [frontend/utils/resume_export.py](frontend/utils/resume_export.py) (ReportLab) is no longer used.
- Streamlit config (theme, hidden auto page list) is in [.streamlit/config.toml](.streamlit/config.toml) at the repo root.
>>>>>>> Stashed changes
- Dependencies: [frontend/requirements.txt](frontend/requirements.txt).
- More detail: [frontend/README.md](frontend/README.md) and [doc/FRONTEND_STRUCTURE.md](doc/FRONTEND_STRUCTURE.md).

### Conventions when adding to the frontend
- New page → add module in `frontend/pages/`, expose a `render()` function, register it in `frontend/pages/__init__.py`, and wire routing/navigation in `frontend/main.py`.
- New reusable UI piece → add to `frontend/components/`, export via `frontend/components/__init__.py`.
- Styling changes go in `frontend/styles/theme.py`, not inline in page modules.
- State is managed via Streamlit's `session_state` — there is no separate state store.

## Backend

<<<<<<< Updated upstream
The backend has two folders:
=======
- **Java 25**, **Spring Boot 4.1**, Maven wrapper (`./mvnw`). MongoDB via Spring Data, Spring Security with JWT, OpenFeign client for the agent service, PDFBox for reading uploaded PDFs, Lombok, springdoc (Swagger UI at `/swagger-ui.html`), Actuator (`/actuator/health`).
- Package `com.learning.resumemaker`, layered: `controller/` → `service/` → `repository/` (Mongo `document/`s), with `model/` (request/response DTOs), `mapper/`, `exception/` (`GlobalExceptionHandler`), `security/`, `client/AgentClient.java`, `aspect/` (logging), `web/` (request-context interceptor), `config/`.
- Endpoints:
  - `/api/auth`: `POST /register`, `POST /login`, `GET /me`
  - `/api/resumes`: list, get, create, update, delete, `POST /upload` (multipart PDF → text → agent `/api/parse`), `GET /{id}/download?template=<id>&format=pdf|tex` (the resume in a template; `pdf` is the default)
  - `/api/templates`: `GET` lists the LaTeX templates
- LaTeX templates: `.tex` files in [src/main/resources/templates/](backend/resumemaker/src/main/resources/templates/), filled by `ResumeTemplateService` with Apache FreeMarker (square-bracket syntax, `ResumeDocument` as the data model; see the header of `classic.tex`). They are found at startup: a file is offered only if it has placeholders (`[=...]`) and parses, so filled samples such as `resume-v1.tex` are skipped. Current templates: `classic.tex` and `modern.tex` (the `resume-v1.tex` layout). To add a template, drop a FreeMarker `.tex` file in that folder and rebuild the backend; its file name is the template id. Use only packages the backend image installs (no `enumitem`, `titlesec`, etc., which are in TeX Live's large "extra" collection); `LatexCompilerTest` compiles every template when `pdflatex` is installed.
- PDF: `LatexCompiler` runs `pdflatex` (`app.latex.command`, env `LATEX_COMMAND`; timeout `app.latex.timeout`) without shell escape, in a temp folder. The backend Docker image installs TeX Live (`texlive-latex-base`, `texlive-fonts-recommended`, `cm-super-minimal`, `lmodern`; about 310 MB). With `make run-backend`, install TeX Live / MacTeX locally, or PDF downloads answer 503 while `.tex` still works. Characters the fonts cannot draw (e.g. Devanagari) are dropped from the PDF with a warning in the log.
  - `/api/applications`: list, create, update, delete
  - `/api/ats`, `/api/summary`: forwarded to the agent service
- JSON uses **snake_case** (`spring.jackson.property-naming-strategy: SNAKE_CASE`).
- Config: [application.yaml](backend/resumemaker/src/main/resources/application.yaml). `JWT_SECRET` and `agent.service.url` (`AGENT_SERVICE_URL` in Docker) are the main settings. Locally, Spring's Docker Compose support starts MongoDB from [compose.yaml](backend/resumemaker/compose.yaml).
- Coding standards: [.github/instructions/development/java.instructions.md](.github/instructions/development/java.instructions.md).
>>>>>>> Stashed changes

- [backend/resumemaker/](backend/resumemaker/): Java Spring Boot API. Scaffold only, no endpoints implemented yet.
- [backend/agents/](backend/agents/): Python agent service (FastAPI + LangGraph). In progress; see the architecture section below.

<<<<<<< Updated upstream
Do not assume an existing API contract. If asked to add backend functionality, confirm with the user which of the two services it belongs to.
=======
- **Python 3.12**, FastAPI, LangChain, LangGraph, LangSmith. Model providers: Anthropic, Gemini, Groq, or a local Ollama server.
  - **FastAPI**: the HTTP endpoints.
  - **LangChain**: model access. `init_chat_model` and the fallback in `core/llm.py`, `SystemMessage`/`HumanMessage` prompts, provider packages `langchain-anthropic`, `langchain-google-genai`, `langchain-groq`, `langchain-ollama`.
  - **LangGraph**: the tailoring workflow (`StateGraph`, `interrupt()` to ask the user, `InMemorySaver` checkpoints).
  - **LangSmith**: optional tracing of every model call and workflow step. No code involved; it is switched on by the `LANGSMITH_*` variables below.
- Code lives in `backend/agents/app/`:
  - `api/`: route classes subclassing `api/base.py`, mounted in `app/main.py`. Endpoints: `POST /api/parse`, `POST /api/ats`, `POST /api/summary`, `POST /api/runs`, `GET /api/runs/{run_id}`, `POST /api/runs/{run_id}/resume`, `GET /health`.
  - `agents/`: LLM-backed agents (subclasses of `agents/base.py`): Gap Analyst, Rewriter, Reviewer (the workflow), plus Resume Parser and Summary Writer (single-call endpoints).
  - `steps/`: deterministic code, no model: JD extraction (`jd.py`), keyword vocabulary (`keywords.py`), ATS scoring (`ats.py`), turning drafts into claims (`claims.py`), grounding check for parsed resumes (`grounding.py`).
  - `graph/`: the LangGraph workflow (`workflow.py`), its state (`state.py`), and `diagram.py`.
  - `core/`: settings (`config.py`), model factory with fallback and per-agent model tiers (`llm.py`), logging, run storage (`persistence.py`).
  - `schemas/`: Pydantic models.
- Config comes from environment variables or `backend/agents/.env` (see [config.py](backend/agents/app/core/config.py)): `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` and/or `GROQ_API_KEY`, or `AGENTS_PROVIDER=ollama`. Other settings use the `AGENTS_` prefix (models per tier, timeouts, retries, log level).
- Provider and fallback: `AGENTS_PROVIDER` picks the main provider; if unset, the first with a key wins (Anthropic, then Gemini, then Groq). When the main model keeps failing (503 overload, 429 quota), the fallback answers: `AGENTS_FALLBACK_MODEL` on the same provider if set, otherwise the default model of the next provider in that order that has a key (e.g. Gemini main + `GROQ_API_KEY` → Groq `openai/gpt-oss-120b`). Ollama is never an automatic fallback.
- Groq `openai/gpt-oss-*` models are reasoning models whose thinking counts against the output limit, so they run at `AGENTS_GROQ_REASONING_EFFORT=low` (default). At higher effort, long replies such as a parsed resume get cut off and the JSON is incomplete.
- LangSmith tracing: set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` (e.g. `resume-maker`) and `LANGSMITH_ENDPOINT` in `backend/agents/.env`. Traces then appear in that LangSmith project. This currently works only in Docker (`make deploy`), where Compose exports `.env` into the environment. With `make run-agent`, `Settings` reads `.env` without exporting it, so LangSmith never sees these variables.
- Runs and checkpoints are **in memory** (`InMemorySaver`): they are lost when the service restarts.
- Conventions: class-based code (route classes, agent base class, workflow class). Coding standards: [.github/instructions/development/python.instructions.md](.github/instructions/development/python.instructions.md).
>>>>>>> Stashed changes

## Planned architecture (multi-agent)

Two backend services (the Spring Boot API is a scaffold only; the Python agent service is in progress):
- **Java Spring Boot API** (`backend/resumemaker/`): CRUD, MongoDB, sessions/chat, SSE relay to the UI.
- **Python agent service** (`backend/agents/`, in progress): FastAPI + **LangGraph**, all agents in one process.

Agents (tool-using, looping): **Gap Analyst**, **Rewriter**, **Reviewer**. Deterministic steps (not agents): parse resume, extract JD, ATS score, export. The code fixes the order of the steps in a LangGraph `StateGraph` (`app/graph/workflow.py`), and the agents share a `WorkflowState`; `ask_user` uses LangGraph `interrupt()` with a checkpointer. The Reviewer fact-checks every rewritten claim against the original resume.

```
  START -> analyze_job -> gap_analyst -> rewriter --(facts missing)--> ask_user --+
                                           ^   \--(otherwise)--> reviewer         |
                                           |                         |            |
                                           +----(rejected, < 3 rounds)           |
                                           +<-------------------------------------+
                                                  (approved or out of rounds) -> finalize -> END

  Deterministic steps (plain code, no model): analyze_job (JobDescriptionExtractor + AtsScorer), finalize
  Agents (model calls): gap_analyst, rewriter, reviewer
  (Research agent: deferred, not part of the current agents)
```

<<<<<<< Updated upstream
Code lives in `backend/agents/app/` (`agents/`, `steps/`, `graph/`, `schemas/`, `core/`, `api/`). The Gap Analyst, Rewriter and Reviewer are implemented in `backend/agents/app/agents/`, and the workflow that connects them is `backend/agents/app/graph/workflow.py`. There is no separate Orchestrator agent: the graph's routing functions decide the next step. `python -m app.graph.diagram` (run from `backend/agents/`) prints the workflow diagram.
=======
`python -m app.graph.diagram` (run from `backend/agents/`) prints the workflow diagram.

### Known gaps
- The frontend's AI run calls (`start_run`, `get_run`, `answer_run` in `api_client.py`) go to `/api/resumes/{id}/runs` and `/api/runs/...` on the Spring Boot API, but the API has no runs controller yet, and `AgentClient` only covers parse, ATS and summary. Runs exist only on the agent service.
- No SSE/streaming: the UI polls the run status.
- Run state is in memory on the agent service.
- LangSmith tracing does not work with `make run-agent` (see the agent service config above): `.env` still has to be loaded into the process environment at startup.
>>>>>>> Stashed changes

### Deferred / future work
- **Research agent**: web search on the company and role to align tone and keywords. Deferred; it would be the only agent with internet access.
- **Cost and latency per run**: open question, to be decided later. Multi-agent runs cost roughly 3-10x a single LLM call. Levers: smaller model for Gap Analyst, cache JD analysis, per-run token budget.

## Running the app

Via Make ([Makefile](Makefile)):
```bash
make build   # pip install -r frontend/requirements.txt
make run     # streamlit run frontend/app.py
make stop    # kill the streamlit process
```
Docker: `make docker-build`, `make docker-run`, `make docker-stop` (builds from `frontend/Dockerfile`).

The app serves at `http://localhost:8501`.

## Working guidelines

- This is an early-stage project — expect gaps (no backend, no auth, no persistence beyond session state yet). Don't assume infrastructure that isn't there; check `product/` and `doc/` for what's planned vs. built.
- Keep changes scoped to the relevant top-level folder (`frontend/`, `backend/`, `doc/`, `product/`) — avoid cross-cutting restructures unless explicitly requested.
- No automated test suite currently exists in this repo; if you add one, document how to run it here.
