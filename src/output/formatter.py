"""Format extracted questions for output"""

from typing import Dict, List
from ..core.constants import ExportFormat

class Formatter:
    """Format questions for various outputs"""
    
    def format_latex(self, questions: List[Dict]) -> str:
        """Format questions as LaTeX document
        
        Args:
            questions: List of questions
            
        Returns:
            LaTeX formatted string
        """
        latex_parts = [
            "\\documentclass[12pt]{article}",
            "\\usepackage{amsmath}",
            "\\usepackage{amssymb}",
            "\\usepackage{enumitem}",
            "\\usepackage{geometry}",
            "\\geometry{a4paper, margin=1in}",
            "",
            "\\title{RD Sharma Class 12 - Extracted Questions}",
            "\\date{\\today}",
            "",
            "\\begin{document}",
            "\\maketitle",
            ""
        ]
        
        for i, question in enumerate(questions, 1):
            latex_parts.append(f"\\section*{{Question {i}}}")
            latex_parts.append(question.get('latex', question.get('text', '')))
            latex_parts.append("")
        
        latex_parts.append("\\end{document}")
        
        return '\n'.join(latex_parts)
    
    def format_markdown(self, questions: List[Dict]) -> str:
        """Format questions as Markdown
        
        Args:
            questions: List of questions
            
        Returns:
            Markdown formatted string
        """
        md_parts = [
            "# RD Sharma Class 12 - Extracted Questions",
            "",
            f"**Total Questions:** {len(questions)}",
            "",
            "---",
            ""
        ]
        
        for i, question in enumerate(questions, 1):
            md_parts.append(f"## Question {i}")
            
            if question.get('number'):
                md_parts.append(f"**Original Number:** {question['number']}")
            
            md_parts.append("")
            md_parts.append("**LaTeX:**")
            md_parts.append(f"```latex\n{question.get('latex', question.get('text', ''))}\n```")
            
            if question.get('page_number'):
                md_parts.append(f"*Page: {question['page_number']}*")
            
            md_parts.append("")
            md_parts.append("---")
            md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def format_json(self, questions: List[Dict]) -> Dict:
        """Format questions as JSON
        
        Args:
            questions: List of questions
            
        Returns:
            JSON-serializable dictionary
        """
        return {
            "total_questions": len(questions),
            "questions": questions,
            "metadata": {
                "extractor": "RD Sharma Question Extractor",
                "version": "1.0.0"
            }
        }