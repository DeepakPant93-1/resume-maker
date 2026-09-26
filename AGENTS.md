# AGENTS.md

This file is the entrypoint for any AI agent (Claude, Copilot, or otherwise) working in this repository. Read it before making changes.

## What this project is

**Resume Maker (ResuAI)** is an AI-powered resume tailoring and optimization platform. Users provide an existing resume and a target job description; the app analyzes the gap between them and interactively rewrites the resume (via chat) to better match the role, then exports it as PDF/DOCX/Markdown.

Full product context (problem statement, features, user journey) lives in [product/README.md](product/README.md). Individual feature specs live in [product/features/](product/features/) (e.g. `RM-01.md`).

## Repository layout

| Path | Purpose |
|---|---|
| [frontend/](frontend/) | The application UI. Built with **Streamlit** (Python). Currently the only implemented layer — see below. |
| [backend/](backend/) | Reserved for the backend/API service. **Currently empty** — not yet implemented. Do not assume backend endpoints exist. |
| [doc/](doc/) | Technical/architecture documentation (structure notes, UI walkthroughs, prototype docs). |
| [product/](product/) | Product requirements: vision, problem statement, features, user journeys. Start here to understand *why* before changing *what*. |
| [.github/agents/](.github/agents/) | AI agent definitions/personas for this repo. |
| [.github/instructions/](.github/instructions/) | Scoped instructions for AI agents (e.g. per-directory or per-task rules). |
| [.github/skills/](.github/skills/) | Reusable AI agent skills for this repo. |
| [.github/prompts/](.github/prompts/) | Saved/reusable prompts for AI agents. |


## Frontend

- Framework: **Streamlit**, Python 3.9.
- Entry point: [frontend/app.py](frontend/app.py) → orchestrator [frontend/main.py](frontend/main.py).
- Structure: `pages/` (one module per screen: dashboard, create_resume, my_resumes, job_match, templates, ai_agents, applications, settings), `components/` (reusable UI pieces), `styles/theme.py` (all CSS/theming), `utils/` (helpers), `assets/` (images/logos).
- Dependencies: [frontend/requirements.txt](frontend/requirements.txt).
- More detail: [frontend/README.md](frontend/README.md) and [doc/FRONTEND_STRUCTURE.md](doc/FRONTEND_STRUCTURE.md).

### Conventions when adding to the frontend
- New page → add module in `frontend/pages/`, expose a `render()` function, register it in `frontend/pages/__init__.py`, and wire routing/navigation in `frontend/main.py`.
- New reusable UI piece → add to `frontend/components/`, export via `frontend/components/__init__.py`.
- Styling changes go in `frontend/styles/theme.py`, not inline in page modules.
- State is managed via Streamlit's `session_state` — there is no separate state store.

## Backend

Not yet implemented. If asked to add backend functionality, confirm with the user whether to scaffold a new service under `backend/` rather than assuming an existing API contract.

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
