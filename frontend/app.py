"""Main Streamlit application"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from pages.extraction import extraction_page
from pages.history import history_page
from pages.settings import settings_page
from components.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="RD Sharma Question Extractor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    .latex-preview {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-family: 'Computer Modern', serif;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Render sidebar
    page = render_sidebar()
    
    # Header
    st.title("📚 RD Sharma Question Extractor")
    st.markdown("**Extract and convert mathematical questions to LaTeX format**")
    st.divider()
    
    # Route to selected page
    if page == "Extract Questions":
        extraction_page()
    elif page == "History":
        history_page()
    elif page == "Settings":
        settings_page()

if __name__ == "__main__":
    main()