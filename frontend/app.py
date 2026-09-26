"""
ResuAI - Resume Builder with AI
Frontend Application Entry Point

Run with: streamlit run frontend/app.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import run

if __name__ == "__main__":
    run()
