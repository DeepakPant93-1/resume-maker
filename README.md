# ResuAI - Resume Builder with AI

AI-powered resume builder for tailoring and optimizing resumes to job descriptions.

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run frontend/app.py
```

The app will open at `http://localhost:8501`

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
python-docx>=0.8.11
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
