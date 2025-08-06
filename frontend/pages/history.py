"""History viewer page"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

from src.utils.file_handler import FileHandler

def history_page():
    """Render history page"""
    
    st.header("Extraction History")
    
    # Load history
    history_file = Path("data/cache/history.json")
    
    if history_file.exists():
        file_handler = FileHandler()
        history = file_handler.load_json(history_file)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            date_filter = st.date_input("Filter by Date")
        
        with col2:
            chapter_filter = st.selectbox(
                "Filter by Chapter",
                ["All"] + list(set(h.get('chapter', '') for h in history))
            )
        
        # Display history
        for entry in reversed(history):
            # Apply filters
            if chapter_filter != "All" and entry.get('chapter') != chapter_filter:
                continue
            
            with st.expander(
                f"{entry['timestamp']} - Chapter {entry['chapter']}, Topic {entry['topic']}"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Questions Extracted", entry['total_questions'])
                
                with col2:
                    st.metric("Processing Time", f"{entry['processing_time']:.2f}s")
                
                with col3:
                    st.metric("Success Rate", f"{entry['success_rate']:.1f}%")
                
                # Re-export options
                if st.button(f"Re-export {entry['id']}", key=entry['id']):
                    st.info("Re-exporting...")
    else:
        st.info("No extraction history available yet.")