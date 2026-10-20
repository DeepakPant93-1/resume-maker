# AGENTS.md

This file is the entrypoint for any AI agent (Claude, Copilot, or otherwise) working in this repository. Read it before making changes.

## What this project is

**Resume Maker (ResuAI)** is an AI-powered resume tailoring and optimization platform. Users upload or build a resume and give a target job description. The app analyzes the gap between them, rewrites the resume to match the role better (asking the user for missing facts along the way), scores it for ATS, and exports it as PDF/DOCX/Markdown.

Full product context (problem statement, features, user journey) lives in [product/README.md](product/README.md). Individual feature specs live in [product/features/](product/features/) (e.g. `RM-01.md`).

## Repository layout

| Path | Purpose |
|---|---|
| [frontend/](frontend/) | Streamlit (Python) UI. Talks only to the Spring Boot API. |
| [backend/resumemaker/](backend/resumemaker/) | Java Spring Boot API: auth (JWT), resumes, applications, ATS and summary endpoints, MongoDB. Calls the agent service. |
| [backend/agents/](backend/agents/) | Python FastAPI + LangGraph agent service: resume parsing, ATS scoring, summary writing, and the multi-agent tailoring workflow. |
| [docker-compose.yml](docker-compose.yml) | Full stack: MongoDB, agents, backend, frontend. |
| `docs/` | Technical documentation (Markdown, Mermaid diagrams). Write new docs here, following [documentation.instructions.md](.github/instructions/documentation/documentation.instructions.md). |
| [doc/](doc/) | Older docs (structure notes, UI walkthroughs, prototype docs). Partly outdated. |
| [product/](product/) | Product requirements: vision, problem statement, features, user journeys. Start here to understand *why* before changing *what*. |
| [.github/agents/](.github/agents/) | AI agent definitions/personas for this repo (`developer.agent.md`). |
| [.github/instructions/](.github/instructions/) | Scoped instructions for AI agents: `development/` (Java, Python), `documentation/`, `review/`, `testing/`. Follow the ones whose `applyTo` matches the files you touch. |
| [.github/skills/](.github/skills/), [.github/prompts/](.github/prompts/) | Reusable skills and prompts (currently empty). |

How the parts talk to each other:

```
  Streamlit UI (:8501) --HTTP + JWT--> Spring Boot API (:8080) --Feign--> Agent service (:8000)
                                              |
                                           MongoDB
```

## Frontend

- Framework: **Streamlit**, Python 3.12+ (the Docker image uses 3.13).
- Entry point: [frontend/app.py](frontend/app.py) → orchestrator [frontend/main.py](frontend/main.py) (sidebar, routing via `PAGES`, login restore).
- Structure: `pages/` (one module per screen: dashboard, create_resume, my_resumes, job_match, templates, ai_agents, applications, settings, plus `login.py` and `ai_run.py` which are not sidebar pages), `components/` (reusable UI pieces), `styles/theme.py` (all CSS/theming), `utils/` (helpers), `assets/` (images/logos).
- Backend access: all HTTP calls go through [frontend/utils/api_client.py](frontend/utils/api_client.py). The base URL comes from `RESUMEMAKER_API_URL` (default `http://localhost:8080`).
- Auth: [frontend/utils/auth.py](frontend/utils/auth.py) keeps the JWT in `session_state` and in a cookie, so a page refresh stays logged in.
- Export: [frontend/utils/resume_export.py](frontend/utils/resume_export.py) builds the PDF/DOCX/Markdown downloads in the frontend.
- Streamlit config (theme, hidden auto page list) is in [.streamlit/config.toml](.streamlit/config.toml) at the repo root.
- Dependencies: [frontend/requirements.txt](frontend/requirements.txt).

### Conventions when adding to the frontend
- New page → add a module in `frontend/pages/` with a `render()` function, register it in `frontend/pages/__init__.py`, and add it to `NAV_ITEMS` / `PAGES` in `frontend/main.py`.
- New backend call → add a function to `frontend/utils/api_client.py`; don't call `requests` from pages.
- New reusable UI piece → add to `frontend/components/`, export via `frontend/components/__init__.py`.
- Styling changes go in `frontend/styles/theme.py`, not inline in page modules.
- UI state lives in Streamlit's `session_state`; persisted data lives in the backend (MongoDB).

## Backend: Spring Boot API (`backend/resumemaker/`)

- **Java 25**, **Spring Boot 4.1**, Maven wrapper (`./mvnw`). MongoDB via Spring Data, Spring Security with JWT, OpenFeign client for the agent service, PDFBox for reading uploaded PDFs, Lombok, springdoc (Swagger UI at `/swagger-ui.html`), Actuator (`/actuator/health`).
- Package `com.learning.resumemaker`, layered: `controller/` → `service/` → `repository/` (Mongo `document/`s), with `model/` (request/response DTOs), `mapper/`, `exception/` (`GlobalExceptionHandler`), `security/`, `client/AgentClient.java`, `aspect/` (logging), `web/` (request-context interceptor), `config/`.
- Endpoints:
  - `/api/auth`: `POST /register`, `POST /login`, `GET /me`
  - `/api/resumes`: list, get, create, update, delete, `POST /upload` (multipart PDF → text → agent `/api/parse`)
  - `/api/applications`: list, create, update, delete
  - `/api/ats`, `/api/summary`: forwarded to the agent service
- JSON uses **snake_case** (`spring.jackson.property-naming-strategy: SNAKE_CASE`).
- Config: [application.yaml](backend/resumemaker/src/main/resources/application.yaml). `JWT_SECRET` and `agent.service.url` (`AGENT_SERVICE_URL` in Docker) are the main settings. Locally, Spring's Docker Compose support starts MongoDB from [compose.yaml](backend/resumemaker/compose.yaml).
- Coding standards: [.github/instructions/development/java.instructions.md](.github/instructions/development/java.instructions.md).

## Backend: Python agent service (`backend/agents/`)

- **Python 3.12**, FastAPI, LangGraph, LangChain. Model providers: Anthropic, Gemini, or a local Ollama server.
- Code lives in `backend/agents/app/`:
  - `api/`: route classes subclassing `api/base.py`, mounted in `app/main.py`. Endpoints: `POST /api/parse`, `POST /api/ats`, `POST /api/summary`, `POST /api/runs`, `GET /api/runs/{run_id}`, `POST /api/runs/{run_id}/resume`, `GET /health`.
  - `agents/`: LLM-backed agents (subclasses of `agents/base.py`): Gap Analyst, Rewriter, Reviewer (the workflow), plus Resume Parser and Summary Writer (single-call endpoints).
  - `steps/`: deterministic code, no model: JD extraction (`jd.py`), keyword vocabulary (`keywords.py`), ATS scoring (`ats.py`), turning drafts into claims (`claims.py`), grounding check for parsed resumes (`grounding.py`).
  - `graph/`: the LangGraph workflow (`workflow.py`), its state (`state.py`), and `diagram.py`.
  - `core/`: settings (`config.py`), model factory with fallback and per-agent model tiers (`llm.py`), logging, run storage (`persistence.py`).
  - `schemas/`: Pydantic models.
- Config comes from environment variables or `backend/agents/.env` (see [config.py](backend/agents/app/core/config.py)): `ANTHROPIC_API_KEY` and/or `GOOGLE_API_KEY`, or `AGENTS_PROVIDER=ollama`. Other settings use the `AGENTS_` prefix (models per tier, timeouts, retries, log level).
- Runs and checkpoints are **in memory** (`InMemorySaver`): they are lost when the service restarts.
- Conventions: class-based code (route classes, agent base class, workflow class). Coding standards: [.github/instructions/development/python.instructions.md](.github/instructions/development/python.instructions.md).

### Tailoring workflow (multi-agent)

The order of the steps is fixed in a LangGraph `StateGraph` ([workflow.py](backend/agents/app/graph/workflow.py)); the model only runs inside the three agent nodes, which share a `WorkflowState`. There is no separate Orchestrator agent: the graph's routing functions (`after_rewrite`, `after_review`) decide the next step. `ask_user` pauses the run with LangGraph `interrupt()` and resumes through the checkpointer. The Reviewer fact-checks every rewritten claim against the original resume.

```
  START -> analyze_job -> gap_analyst -> rewriter --(facts missing)--> ask_user --+
                                           ^   \--(otherwise)--> reviewer         |
                                           |                         |            |
                                           +----(rejected, < 3 rounds)           |
                                           +<-------------------------------------+
                                                  (approved or out of rounds) -> finalize -> END

  Deterministic steps (plain code, no model): analyze_job (JobDescriptionExtractor + AtsScorer), finalize
  Agents (model calls): gap_analyst, rewriter, reviewer
  Limits: 3 rewrite rounds, 2 question rounds
```

`python -m app.graph.diagram` (run from `backend/agents/`) prints the workflow diagram.

### Known gaps
- The frontend's AI run calls (`start_run`, `get_run`, `answer_run` in `api_client.py`) go to `/api/resumes/{id}/runs` and `/api/runs/...` on the Spring Boot API, but the API has no runs controller yet, and `AgentClient` only covers parse, ATS and summary. Runs exist only on the agent service.
- No SSE/streaming: the UI polls the run status.
- Run state is in memory on the agent service.

### Deferred / future work
- **Research agent**: web search on the company and role to align tone and keywords. Deferred; it would be the only agent with internet access.
- **Cost and latency per run**: open question. Multi-agent runs cost roughly 3-10x a single LLM call. Levers already in place: per-agent model tiers (`AGENTS_REWRITE_MODEL`, etc.) and a fallback model. Still open: caching JD analysis, a per-run token budget.

## Running the app

All commands run from the repo root (`make help` lists them; `backend/Makefile` and `backend/resumemaker/Makefile` forward to the root one).

| Part | Port | Start | Stop |
|---|---|---|---|
| Frontend | 8501 | `make build` (first time), `make run` | `make stop` |
| Spring Boot API | 8080 | `make run-backend` (needs Java 25 and Docker for MongoDB) | `make stop-backend` |
| Agent service | 8000 | `make run-agent` (needs `backend/agents/.venv` and a model key in `backend/agents/.env`) | `make stop-agent` |

`make restart-backend` / `make restart-agent` stop and start a service. Agent service setup:
```bash
cd backend/agents && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Full stack in Docker ([docker-compose.yml](docker-compose.yml)): `make deploy`, `make deploy-status`, `make deploy-logs` (`SERVICE=backend` for one), `make deploy-stop`. MongoDB listens on host port 27018 in this setup.

Frontend-only Docker image: `make docker-build`, `make docker-run`, `make docker-stop`.

## Tests

```bash
cd backend/agents && .venv/bin/pytest            # agent service (pytest, tests/)
cd backend/resumemaker && ./mvnw test            # Spring Boot API (JUnit, src/test/)
```

The frontend has no automated tests. Add tests next to the code you change, following [.github/instructions/testing/testing.instructions.md](.github/instructions/testing/testing.instructions.md).

## Working guidelines

- Check `product/` for what is planned and the code for what is built; the READMEs and `doc/` are partly out of date.
- Keep changes scoped to the relevant top-level folder (`frontend/`, `backend/resumemaker/`, `backend/agents/`, `doc/`, `product/`). A feature that crosses services (frontend → API → agents) touches each layer in turn: keep the API contract (snake_case JSON) consistent across them.
- The frontend never calls the agent service directly; new AI features go through the Spring Boot API.
- Never commit secrets: `backend/agents/.env` is gitignored, and `JWT_SECRET` must be overridden outside local development.
