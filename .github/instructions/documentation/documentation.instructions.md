---
name: Technical Documentation
description: Standards for AI agents writing or updating the technical documentation of this repository in the docs/ folder.
applyTo: "docs/**/*.md"
---

# Technical Documentation Instructions

## Location & Format
- All documentation lives in the `docs/` folder at the repository root. Do not add docs elsewhere (`product/` holds product requirements; `README.md` files only cover setup).
- Every document is a Markdown (`.md`) file. No `.txt`, `.docx`, `.pdf` or HTML docs.
- One topic per file. Use lowercase kebab-case file names that say what the doc covers, e.g. `architecture.md`, `agent-workflow.md`, `resume-upload-flow.md`, `api-reference.md`.
- Group related docs in subfolders when there are several on one area, e.g. `docs/backend/`, `docs/agents/`, `docs/frontend/`.
- Keep `docs/README.md` as the index: one line per document with a relative link and a one-sentence description. Add the new doc there whenever you create one.

## Focus: Technical Content
- Write for developers working on the code. Explain how the application works, not what it offers the user. Product vision, user journeys and feature requirements belong in `product/`, not in `docs/`.
- Cover the technical aspects:
  - architecture: the services (Streamlit frontend, Spring Boot API, Python agent service, MongoDB) and how they talk to each other
  - request and data flows across those services
  - components, classes and modules and what each is responsible for
  - API endpoints: method, path, request/response body, status codes, auth
  - data models: Mongo documents, DTOs, Pydantic schemas, the LangGraph `WorkflowState`
  - configuration: environment variables, `application.yaml`, `.env`, ports
  - design decisions and their trade-offs (why, not only what)
  - limitations and known gaps

## Code Is the Source of Truth
- Read the relevant code before writing. Every statement in a doc must be verifiable in the code: class and method names, endpoint paths, field names, env vars, ports, limits.
- Use names exactly as they appear in the code (`ResumeUploadService`, `POST /api/resumes/upload`, `AGENTS_PROVIDER`, `MAX_REWRITE_ROUNDS`). Do not paraphrase or invent names.
- Link to the source with a relative path from the doc, e.g. `[ResumeUploadService.java](../backend/resumemaker/src/main/java/com/learning/resumemaker/service/ResumeUploadService.java)`, so readers can jump to it.
- Document only what is built. If you mention something planned, label it clearly (a "Planned" or "Known gaps" section), and never describe it as working.
- If the code and an existing doc disagree, the code wins: fix the doc.
- Never copy secrets, API keys, tokens, real user data or real resume content into a doc. Use obvious placeholders (`<your-api-key>`, `jane@example.com`).

## Diagrams (Mermaid)
- Draw diagrams with Mermaid, embedded in the Markdown file in a ` ```mermaid ` code block. Do not add image files for diagrams.
- Pick the diagram type that fits:

  | To show | Mermaid type |
  |---|---|
  | Architecture: services, databases, external providers | `flowchart` with `subgraph`s |
  | A request crossing services (UI → API → agents → DB) | `sequenceDiagram` |
  | Workflow steps and branches (e.g. the LangGraph workflow) | `flowchart` |
  | Status lifecycle (e.g. a run: running, waiting_for_user, completed, failed) | `stateDiagram-v2` |
  | Classes and their relationships | `classDiagram` |
  | Mongo documents and their links | `erDiagram` |

- Node, participant and state names must match the code (class, service, node or endpoint names).
- Keep each diagram focused on one idea and small enough to read (about 15 nodes at most). Split large ones.
- Put one sentence before each diagram saying what it shows, and explain anything non-obvious after it.
- Quote labels that contain special characters (`A["POST /api/parse"]`). Do not add colors or custom styling.
- Example, a sequence diagram of the resume upload:

  ```mermaid
  sequenceDiagram
      participant UI as Streamlit UI
      participant API as ResumeController
      participant SVC as ResumeUploadService
      participant AG as Agent service
      participant DB as MongoDB

      UI->>API: POST /api/resumes/upload (PDF, JWT)
      API->>SVC: uploadResume(file)
      SVC->>SVC: PdfTextExtractor.extract()
      SVC->>AG: POST /api/parse (text)
      AG-->>SVC: parsed resume JSON
      SVC->>DB: ResumeService.createResume() saves ResumeDocument
      SVC-->>API: ResumeResponse
      API-->>UI: 200 OK (ResumeResponse)
  ```

## Code Snippets
- Always put code, commands, config and payloads in a fenced code block with the language tag: ` ```java `, ` ```python `, ` ```yaml `, ` ```json `, ` ```bash `, ` ```http `, ` ```mermaid `. Use ` ```text ` for plain output. Never leave a fence without a language.
- Use inline backticks for names in prose: classes, methods, files, endpoints, env vars.
- Keep snippets short: show only the lines that explain the point, and link to the full file. Do not paste whole files.
- Snippets must match the current code. Mark shortened code with a `// ...` or `# ...` comment.
- Shell commands must be copy-pasteable and say where they run (default: the repository root), e.g.

  ```bash
  cd backend/agents && .venv/bin/pytest
  ```

## Document Structure
- Start with a `#` title and a two-to-three-sentence overview of what the doc covers and who needs it.
- Then use `##` sections in a logical order, for example: Overview → Architecture/Flow (with diagram) → Components → API/Data → Configuration → Limitations → Related docs.
- Use tables for lists of endpoints, fields, env vars and config options.
- End with a "Related docs" section linking to other docs in `docs/` and to the relevant code folders.

## Writing Style
- Clear, concise, plain English. Present tense, active voice ("The API forwards the text to the agent service").
- Define a term the first time you use it (e.g. ATS, JD, claim, checkpointer).
- No marketing language and no emojis.
- Prefer short paragraphs and bullet lists over long prose.

## Keeping Docs Up to Date
- When a change alters behavior that a doc in `docs/` describes (endpoints, flows, config, data models), update that doc in the same change.
- When you add or remove a document, update `docs/README.md`.
- If the change also affects project-level context (services, commands, env vars), update `AGENTS.md` as well.
