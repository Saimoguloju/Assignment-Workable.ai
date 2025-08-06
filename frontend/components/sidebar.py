"""Sidebar component"""

import streamlit as st

def render_sidebar():
    """Render sidebar navigation
    
    Returns:
        Selected page name
    """
    with st.sidebar:
        st.title("Navigation")
        
        # Page selection
        page = st.radio(
            "Select Page",
            ["Extract Questions", "History", "Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats
        st.subheader("Quick Stats")
        
        # These would be loaded from cache/database
        st.metric("Total Extractions", "0")
        st.metric("Questions in Database", "0")
        st.metric("Last Extraction", "N/A")
        
        st.divider()
        
        # Help section
        with st.expander("Help"):
            st.markdown("""
            **How to use:**
            1. Upload a PDF file
            2. Select chapter and topic
            3. Click Extract Questions
            4. Export in desired format
            
            **Supported formats:**
            - LaTeX (.tex)
            - Markdown (.md)
            - JSON (.json)
            - PDF (requires LaTeX)
            """)
        
        st.divider()
        
        # About
        st.caption("RD Sharma Question Extractor v1.0.0")
        st.caption("Powered by Google Gemini")
    
    return page