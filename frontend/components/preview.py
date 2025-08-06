"""LaTeX preview component"""

import streamlit as st
import base64

def render_latex_preview(latex_code: str):
    """Render LaTeX preview
    
    Args:
        latex_code: LaTeX code to preview
    """
    # For simple inline math, we can use st.latex
    if latex_code.startswith('$') or latex_code.startswith('\\['):
        st.latex(latex_code)
    else:
        # For complex LaTeX, show code with syntax highlighting
        st.code(latex_code, language='latex')
        
        # Option to render using online service
        if st.button("Render LaTeX", key=f"render_{hash(latex_code)}"):
            # This would call an online LaTeX rendering service
            # For now, just show the code
            st.info("LaTeX rendering requires external service setup")