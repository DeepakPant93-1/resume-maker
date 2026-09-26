# ResuAI Frontend Module

Professional, modular Streamlit frontend for the Resume Builder application.

## 📁 Project Structure

```
resume-maker/
├── app.py                    (old monolithic version)
├── app_new.py               (NEW - uses modular frontend)
├── frontend/                (NEW - modular frontend structure)
│   ├── __init__.py
│   ├── main.py              (App orchestrator & routing)
│   ├── README.md            (This file)
│   ├── pages/               (Page components)
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── create_resume.py
│   │   ├── my_resumes.py
│   │   ├── job_match.py
│   │   ├── templates.py
│   │   ├── ai_agents.py
│   │   ├── applications.py
│   │   └── settings.py
│   ├── components/          (Reusable UI components)
│   │   └── __init__.py
│   ├── styles/              (CSS & theming)
│   │   ├── __init__.py
│   │   └── theme.py         (All styling & CSS)
│   ├── utils/               (Utility functions)
│   │   └── __init__.py
│   └── assets/              (Images, logos, etc.)
│
├── pages/                   (Old modular structure)
│   └── create_resume/
│
├── requirements.txt
└── frontend_structure.txt   (This structure)
```

## 🚀 Quick Start

### Run the NEW modular version:
```bash
cd resume-maker
streamlit run app_new.py
```

### Run the old version:
```bash
streamlit run app.py
```

---

## 📚 Architecture

### Core Components

#### 1. **main.py** - Application Orchestrator
- App initialization & configuration
- Session state management
- Page routing
- Sidebar navigation
- Footer rendering

#### 2. **pages/** - Page Modules
Each page is a separate module with a `render()` function:
- `dashboard.py` - Home screen with metrics
- `create_resume.py` - Resume creation options
- `my_resumes.py` - Resume editor
- `job_match.py` - Job-resume matching
- `templates.py` - Template gallery
- `ai_agents.py` - AI agents workspace
- `applications.py` - Application tracker
- `settings.py` - User settings & profile

#### 3. **styles/theme.py** - UI Styling
Centralized CSS with:
- Color scheme (Purple gradient: #667eea → #764ba2)
- Component styles (.metric-box, .resume-card, .create-card, etc.)
- Responsive design
- Hover effects & transitions

#### 4. **components/** - Reusable Components
(To be populated with shared UI components)

#### 5. **utils/** - Helper Functions
(To be populated with utility functions)

---

## 🎨 Design System

### Colors
- **Primary:** Purple Gradient (#667eea → #764ba2)
- **Success:** Green (#4caf50)
- **Neutral:** Gray (#666, #999, #333)
- **Background:** Light (#f5f7ff → #f8f9fa)

### Component Styles
- `.metric-box` - Large metric displays
- `.resume-card` - Content cards
- `.ats-badge` - ATS score badges
- `.create-card` - Option cards
- `.step-box` - Step indicators
- `.step-number` - Numbered circles
- `.live-preview` - Resume preview

---

## 🔄 Routing & Navigation

### Page Navigation
```
sidebar.button → st.session_state.page = "PageName" → render_page()
```

### Session State
```python
st.session_state = {
    "page": "Dashboard",  # Current page
    "resume_data": {},    # Form data
    "resumes": [...]      # User's resumes
}
```

---

## 📋 Page Details

### Dashboard
- Welcome greeting
- Quick action buttons
- 4 metric boxes (Resumes, Applications, ATS Score, Credits)
- Resume cards with ATS badges

### Create Resume
- 3 options: Upload, Build from Scratch, Generate with AI
- 6-step recommended flow indicator

### My Resumes (Editor)
- Section selector (Profile, Experience, Education, Skills)
- Content editor
- Live preview panel
- AI Improve, ATS Check, Save buttons

### Job Match
- Job description input
- Match score display
- Missing skills & suggestions

### Templates
- Template gallery
- Filter options
- Use template button

### AI Agents
- Agent cards
- Status indicators (Active/Idle)
- Agent descriptions

### Applications
- Application tracker table
- Company, role, ATS match, stage
- Action buttons

### Settings
- Profile management
- Preferences (AI style, template, notifications)
- Pricing plans

---

## ✨ Features

✅ Modular page-based architecture  
✅ Centralized routing & navigation  
✅ Unified styling system  
✅ Session state management  
✅ Responsive design  
✅ Professional UI with gradients & animations  
✅ Easy to extend & maintain  
✅ Component reusability  

---

## 🔧 How to Add a New Page

1. Create `frontend/pages/new_page.py`:
```python
import streamlit as st

def render():
    """Render new page"""
    st.markdown("# New Page")
    # Add content...
```

2. Update `frontend/pages/__init__.py`:
```python
from . import new_page
__all__ = [..., "new_page"]
```

3. Update `frontend/main.py` routing:
```python
elif page == "NewPage":
    new_page.render()
```

4. Add to sidebar in `render_sidebar()`:
```python
"📄 New Page": "NewPage"
```

---

## 📦 Dependencies

```
streamlit>=1.28.1
pandas>=2.1.1
python-docx>=0.8.11
pypdf>=3.17.1
```

---

## 🚀 Future Enhancements

- [ ] Add reusable components in `components/`
- [ ] Add utility functions in `utils/`
- [ ] Database integration for persistence
- [ ] Claude API integration for AI features
- [ ] Export to PDF/DOCX
- [ ] Authentication system
- [ ] Dark mode toggle
- [ ] Internationalization (i18n)
- [ ] Unit tests
- [ ] E2E tests

---

## 📝 Notes

- Each page module is self-contained
- `render()` function is the entry point for each page
- Session state persists during the user's session
- All styling is in `styles/theme.py` for easy maintenance
- Easy to debug - trace issues to specific page modules

---

## 🤝 Contributing

When modifying or extending:
1. Keep pages modular
2. Add styles to `theme.py` only
3. Update sidebar navigation
4. Test on multiple screen sizes
5. Update this README

---

## 📞 Support

For issues or questions:
1. Check the page-specific files
2. Review `theme.py` for styling issues
3. Check session state in `main.py`
4. See `pages/__init__.py` for routing
