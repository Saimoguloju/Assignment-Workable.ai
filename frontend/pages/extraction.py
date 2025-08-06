"""Question extraction page"""

import streamlit as st
from pathlib import Path
import tempfile
from typing import Optional

from src.rag.rag_pipeline import RAGPipeline
from src.core.constants import CHAPTER_TOPICS
from src.output.exporter import Exporter
from frontend.components.upload import render_upload
from frontend.components.preview import render_latex_preview

def extraction_page():
    """Render extraction page"""
    
    st.header("Extract Questions")
    
    # File upload
    uploaded_file = render_upload()
    
    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = Path(tmp.name)
        
        # Chapter and topic selection
        col1, col2 = st.columns(2)
        
        with col1:
            chapters = list(CHAPTER_TOPICS.keys())
            chapter = st.selectbox(
                "Select Chapter",
                chapters,
                format_func=lambda x: f"Chapter {x}: {CHAPTER_TOPICS[x]['name']}"
            )
        
        with col2:
            if chapter:
                topics = list(CHAPTER_TOPICS[chapter]['topics'].items())
                topic = st.selectbox(
                    "Select Topic",
                    [t[0] for t in topics],
                    format_func=lambda x: f"{x}: {CHAPTER_TOPICS[chapter]['topics'][x]}"
                )
        
        # Extraction options
        with st.expander("Advanced Options"):
            include_illustrations = st.checkbox("Include Illustrations", value=True)
            include_examples = st.checkbox("Include Examples", value=True)
            include_exercises = st.checkbox("Include Exercises", value=True)
            use_ocr = st.checkbox("Use OCR for scanned pages", value=True)
        
        # Extract button
        if st.button("🚀 Extract Questions", type="primary"):
            with st.spinner("Extracting questions... This may take a few minutes."):
                try:
                    # Initialize pipeline
                    pipeline = RAGPipeline()
                    
                    # Process PDF
                    results = pipeline.process_pdf(
                        pdf_path=pdf_path,
                        chapter=chapter,
                        topic=topic
                    )
                    
                    # Store in session state
                    st.session_state['extraction_results'] = results
                    
                    st.success(f"✅ Extracted {results['total_questions']} questions!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display results
        if 'extraction_results' in st.session_state:
            results = st.session_state['extraction_results']
            
            st.subheader("Extraction Results")
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", results['total_questions'])
            with col2:
                st.metric("Chapter", results['chapter'])
            with col3:
                st.metric("Topic", results['topic'])
            
            # Questions display
            st.subheader("Extracted Questions")
            
            # Filter options
            filter_type = st.selectbox(
                "Filter by Type",
                ["All"] + list(set(q['question_type'] for q in results['questions']))
            )
            
            # Display questions
            filtered_questions = results['questions']
            if filter_type != "All":
                filtered_questions = [
                    q for q in results['questions'] 
                    if q['question_type'] == filter_type
                ]
            
            for i, question in enumerate(filtered_questions, 1):
                with st.expander(f"Question {i} - {question.get('question_type', 'Unknown')}"):
                    # Original text
                    st.markdown("**Original Text:**")
                    st.text(question['original_text'])
                    
                    # LaTeX preview
                    st.markdown("**LaTeX Format:**")
                    render_latex_preview(question['latex'])
                    
                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Page: {question.get('page_number', 'N/A')}")
                    with col2:
                        st.caption(f"Number: {question.get('number', 'N/A')}")
                    with col3:
                        st.caption(f"Confidence: {question.get('confidence', 0):.2f}")
            
            # Export options
            st.subheader("Export Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            exporter = Exporter()
            
            with col1:
                if st.button("📄 Export as LaTeX"):
                    latex_content = exporter.export_latex(results['questions'])
                    st.download_button(
                        label="Download LaTeX",
                        data=latex_content,
                        file_name=f"questions_{results['chapter']}_{results['topic']}.tex",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("📝 Export as Markdown"):
                    md_content = exporter.export_markdown(results['questions'])
                    st.download_button(
                        label="Download Markdown",
                        data=md_content,
                        file_name=f"questions_{results['chapter']}_{results['topic']}.md",
                        mime="text/markdown"
                    )
            
            with col3:
                if st.button("📊 Export as JSON"):
                    json_content = exporter.export_json(results['questions'])
                    st.download_button(
                        label="Download JSON",
                        data=json_content,
                        file_name=f"questions_{results['chapter']}_{results['topic']}.json",
                        mime="application/json"
                    )
            
            with col4:
                if st.button("📑 Export as PDF"):
                    # This would require LaTeX compilation
                    st.info("PDF export requires LaTeX installation")