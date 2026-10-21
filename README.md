# ResuAI - Resume Builder with AI

AI-powered resume builder for tailoring and optimizing resumes to job descriptions.

## 🚀 Quick Start

The app has three parts. Start each in its own terminal (all commands run from the repo root; `make help` lists them).

| Part | Port | Start | Stop |
|------|------|-------|------|
| Frontend (Streamlit) | 8501 | `make run` | `make stop` |
| Spring Boot API (`backend/resumemaker`) | 8080 | `make run-backend` | `make stop-backend` |
| Python agent service (`backend/agents`) | 8000 | `make run-agent` | `make stop-agent` |

`make restart-backend` and `make restart-agent` stop and then start the service.

### 1. Frontend
```bash
make build   # pip install -r frontend/requirements.txt (first time only)
make run     # http://localhost:8501
```

### 2. Backend (Spring Boot API)
Needs Java and Docker. `make run-backend` runs `./mvnw spring-boot:run` from `backend/resumemaker`, and Spring's Docker Compose support starts MongoDB for you.
```bash
make run-backend   # http://localhost:8080
```
If it fails with "Port 8080 was already in use", run `make stop-backend` (or `make restart-backend`).

### 3. Agent service (Python)
Create the virtualenv once, then add your model key:
```bash
cd backend/agents
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
Create `backend/agents/.env` with `ANTHROPIC_API_KEY=...` and/or `GOOGLE_API_KEY=...`. For a local Ollama server, set `AGENTS_PROVIDER=ollama` instead. With both keys set, `AGENTS_PROVIDER` picks the provider.
```bash
make run-agent   # http://localhost:8000
```
If the port is stuck, run `make stop-agent` (or `make restart-agent`).

### Run everything
Start the Spring Boot API and the agent service first, then the frontend: `make run-backend`, `make run-agent`, `make run`.

### Docker (frontend only)
```bash
make docker-build
make docker-run    # http://localhost:8501
make docker-stop
```

---

## 📁 Project Structure

```
resume-maker/
├── frontend/                   ✅ ALL CODE HERE
│   ├── app.py                 (Entry point)
│   ├── main.py                (App orchestrator)
│   ├── README.md              (Frontend docs)
│   │
│   ├── pages/                 (8 page modules)
│   │   ├── dashboard.py
│   │   ├── create_resume.py
│   │   ├── my_resumes.py
│   │   ├── job_match.py
│   │   ├── templates.py
│   │   ├── ai_agents.py
│   │   ├── applications.py
│   │   └── settings.py
│   │
│   ├── styles/                (Theming & CSS)
│   │   └── theme.py
│   │
│   ├── components/            (Reusable components)
│   ├── utils/                 (Helper functions)
│   └── assets/                (Images, logos)
│
├── requirements.txt
└── README.md                  (This file)
```

---

## ✨ Features

🏠 **Dashboard** - Home with metrics and resume cards  
➕ **Create Resume** - 3 methods: upload, build, AI generate  
📋 **Resume Editor** - Edit with live preview  
🎯 **Job Match** - Compare resume vs job description  
🎨 **Templates** - 6 professional templates  
🤖 **AI Agents** - 8 specialized AI agents  
📊 **Applications** - Track job applications  
⚙️ **Settings** - Profile and preferences  

---

## 🎯 Pages

| Page | Purpose |
|------|---------|
| Dashboard | Home screen with metrics |
| Create Resume | Start new resume (3 options) |
| My Resumes | Edit resume with live preview |
| Job Match | Match resume to job description |
| Templates | Browse & select resume templates |
| AI Agents | Specialized AI agent workspace |
| Applications | Job application tracker |
| Settings | User profile & preferences |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Styling:** Custom CSS in `frontend/styles/theme.py`
- **Architecture:** Modular pages-based
- **State Management:** Streamlit session_state

---

## 📚 Documentation

- **Frontend Docs:** See `/frontend/README.md`
- **Frontend Structure:** Clean, modular organization
- **Entry Point:** `/frontend/app.py`
- **Orchestrator:** `/frontend/main.py`

---

## 🚀 Next Steps

1. ✅ Run the frontend app
2. ⬜ Add backend API (`/backend/`)
3. ⬜ Connect Claude API for AI features
4. ⬜ Add database persistence
5. ⬜ Add authentication
6. ⬜ Deploy to production

---

## 📝 Development

### Add a New Page

1. Create `frontend/pages/new_page.py`
2. Add `render()` function
3. Update `frontend/pages/__init__.py`
4. Add routing in `frontend/main.py`
5. Add to sidebar navigation

### Modify Styling

All CSS is in `frontend/styles/theme.py`. Update there for:
- Colors
- Component styles
- Animations
- Responsive design

### Add Reusable Component

1. Create component in `frontend/components/`
2. Import in `frontend/components/__init__.py`
3. Use in page modules

---

## 📦 Requirements

```
streamlit>=1.28.1
pandas>=2.1.1
pypdf>=3.17.1
```

---

## 🤝 Contributing

1. Work in feature branches
2. Update `/frontend/` code only
3. Keep pages modular
4. Add documentation

---

## 📞 Support

- Check `/frontend/README.md` for detailed frontend docs
- Review specific page module for feature details
- Check `frontend/styles/theme.py` for styling issues

---

**Built with ❤️ by ResuAI Team**
