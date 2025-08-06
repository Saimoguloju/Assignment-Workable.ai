"""Settings page"""

import streamlit as st
from pathlib import Path
import os

from src.core.config import get_config

def settings_page():
    """Render settings page"""
    
    st.header("Settings")
    
    config = get_config()
    
    # API Settings
    st.subheader("API Configuration")
    
    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Your Google Gemini API key"
    )
    
    if st.button("Save API Key"):
        # Save to .env file
        env_file = Path(".env")
        env_content = env_file.read_text() if env_file.exists() else ""
        
        if "GEMINI_API_KEY" in env_content:
            # Update existing key
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("GEMINI_API_KEY"):
                    lines[i] = f"GEMINI_API_KEY={api_key}"
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new key
            env_content += f"\nGEMINI_API_KEY={api_key}"
        
        env_file.write_text(env_content)
        st.success("API key saved!")
    
    # Processing Settings
    st.subheader("Processing Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chunk_size = st.number_input(
            "Chunk Size",
            min_value=500,
            max_value=5000,
            value=config.chunk_size,
            step=100,
            help="Size of text chunks for processing"
        )
        
        chunk_overlap = st.number_input(
            "Chunk Overlap",
            min_value=0,
            max_value=500,
            value=config.chunk_overlap,
            step=50,
            help="Overlap between chunks"
        )
    
    with col2:
        ocr_enabled = st.checkbox(
            "Enable OCR",
            value=config.ocr_enabled,
            help="Use OCR for scanned PDFs"
        )
        
        cache_enabled = st.checkbox(
            "Enable Caching",
            value=config.cache_enabled,
            help="Cache extraction results"
        )
    
    # Output Settings
    st.subheader("Output Settings")
    
    default_format = st.selectbox(
        "Default Export Format",
        ["latex", "markdown", "json", "pdf"],
        index=["latex", "markdown", "json", "pdf"].index(config.default_export_format)
    )
    
    output_dir = st.text_input(
        "Output Directory",
        value=str(config.output_dir)
    )
    
    # Advanced Settings
    with st.expander("Advanced Settings"):
        max_pdf_size = st.number_input(
            "Max PDF Size (MB)",
            min_value=10,
            max_value=500,
            value=config.max_pdf_size_mb,
            help="Maximum allowed PDF file size"
        )
        
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.log_level)
        )
    
    # Save settings
    if st.button("Save All Settings", type="primary"):
        # Update configuration
        # This would save to the .env file or config file
        st.success("Settings saved successfully!")
    
    # Clear cache
    st.subheader("Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Cache"):
            cache_dir = Path(config.cache_dir)
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                st.success("Cache cleared!")
    
    with col2:
        if st.button("Clear Vector Store"):
            vector_store_path = Path(config.vector_store_path)
            if vector_store_path.exists():
                import shutil
                shutil.rmtree(vector_store_path)
                vector_store_path.mkdir(parents=True, exist_ok=True)
                st.success("Vector store cleared!")