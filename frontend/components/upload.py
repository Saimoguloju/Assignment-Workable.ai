"""File upload component"""

import streamlit as st
from pathlib import Path

def render_upload():
    """Render file upload component
    
    Returns:
        Uploaded file object or None
    """
    st.subheader("Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose RD Sharma PDF file",
        type=['pdf'],
        help="Upload the RD Sharma Class 12 textbook PDF"
    )
    
    if uploaded_file:
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Name", uploaded_file.name)
        
        with col2:
            size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("File Size", f"{size_mb:.2f} MB")
        
        with col3:
            st.metric("Type", uploaded_file.type)
    
    return uploaded_file