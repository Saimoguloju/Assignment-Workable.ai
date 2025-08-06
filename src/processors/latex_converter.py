"""Convert mathematical expressions to LaTeX format"""

import re
import logging
from typing import Dict, List, Optional, Tuple

from ..core.constants import LATEX_DELIMITERS, MATH_SYMBOLS

class LaTeXConverter:
    """Convert text and math expressions to LaTeX"""
    
    def __init__(self):
        """Initialize LaTeX converter"""
        self.logger = logging.getLogger(__name__)
    
    def convert(self, text: str, math_mode: str = "inline") -> str:
        """Convert text to LaTeX format
        
        Args:
            text: Text to convert
            math_mode: Type of math mode (inline, display, equation)
            
        Returns:
            LaTeX formatted text
        """
        # First, identify and protect existing LaTeX
        text = self._protect_existing_latex(text)
        
        # Convert mathematical expressions
        text = self._convert_math_expressions(text)
        
        # Convert special characters
        text = self._convert_special_characters(text)
        
        # Apply math mode delimiters
        text = self._apply_math_mode(text, math_mode)
        
        # Format for LaTeX document
        text = self._format_for_document(text)
        
        return text
    
    def _protect_existing_latex(self, text: str) -> str:
        """Protect existing LaTeX commands from conversion
        
        Args:
            text: Text with potential LaTeX
            
        Returns:
            Text with protected LaTeX
        """
        # Mark existing LaTeX commands
        latex_commands = re.findall(r'\\[a-zA-Z]+(?:\{[^}]*\})*', text)
        
        for i, cmd in enumerate(latex_commands):
            placeholder = f"__LATEX_CMD_{i}__"
            text = text.replace(cmd, placeholder)
        
        # Store for later restoration
        self._protected_commands = latex_commands
        
        return text
    
    def _convert_math_expressions(self, text: str) -> str:
        """Convert mathematical expressions to LaTeX
        
        Args:
            text: Text with math expressions
            
        Returns:
            Text with LaTeX math
        """
        # Convert fractions
        text = self._convert_fractions(text)
        
        # Convert exponents and subscripts
        text = self._convert_exponents_subscripts(text)
        
        # Convert roots
        text = self._convert_roots(text)
        
        # Convert integrals and sums
        text = self._convert_integrals_sums(text)
        
        # Convert matrices
        text = self._convert_matrices(text)
        
        # Convert probability notation
        text = self._convert_probability(text)
        
        return text
    
    def _convert_fractions(self, text: str) -> str:
        """Convert fractions to LaTeX format
        
        Args:
            text: Text with fractions
            
        Returns:
            Text with LaTeX fractions
        """
        # Simple fractions like 1/2
        text = re.sub(r'(\d+)\s*/\s*(\d+)', r'\\frac{\1}{\2}', text)
        
        # Complex fractions with parentheses
        text = re.sub(r'\(([^)]+)\)\s*/\s*\(([^)]+)\)', r'\\frac{\1}{\2}', text)
        
        # Fractions with variables
        text = re.sub(r'([a-zA-Z]+)\s*/\s*([a-zA-Z]+)', r'\\frac{\1}{\2}', text)
        
        return text
    
    def _convert_exponents_subscripts(self, text: str) -> str:
        """Convert exponents and subscripts
        
        Args:
            text: Text with exponents/subscripts
            
        Returns:
            Converted text
        """
        # Exponents
        text = re.sub(r'([a-zA-Z0-9])\^([a-zA-Z0-9]+)', r'\1^{\2}', text)
        text = re.sub(r'([a-zA-Z0-9])\^([+-]?\d+)', r'\1^{\2}', text)
        
        # Subscripts
        text = re.sub(r'([a-zA-Z])_([a-zA-Z0-9]+)', r'\1_{\2}', text)
        text = re.sub(r'([a-zA-Z])_(\d+)', r'\1_{\2}', text)
        
        # Special cases like x^2, x^3
        text = re.sub(r'\b([xyz])\s*\^\s*2\b', r'\1^2', text)
        text = re.sub(r'\b([xyz])\s*\^\s*3\b', r'\1^3', text)
        
        return text
    
    def _convert_roots(self, text: str) -> str:
        """Convert root expressions
        
        Args:
            text: Text with roots
            
        Returns:
            Converted text
        """
        # Square roots
        text = re.sub(r'√\s*([a-zA-Z0-9]+)', r'\\sqrt{\1}', text)
        text = re.sub(r'sqrt\s*\(([^)]+)\)', r'\\sqrt{\1}', text)
        
        # Nth roots
        text = re.sub(r'(\d+)th\s+root\s+of\s+([a-zA-Z0-9]+)', r'\\sqrt[\1]{\2}', text)
        
        return text
    
    def _convert_integrals_sums(self, text: str) -> str:
        """Convert integrals and summations
        
        Args:
            text: Text with integrals/sums
            
        Returns:
            Converted text
        """
        # Integrals
        text = re.sub(r'∫', r'\\int', text)
        text = re.sub(r'integral\s+from\s+([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)',
                     r'\\int_{\1}^{\2}', text)
        
        # Summations
        text = re.sub(r'Σ', r'\\sum', text)
        text = re.sub(r'sum\s+from\s+([a-zA-Z0-9]+)\s*=\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)',
                     r'\\sum_{\1=\2}^{\3}', text)
        
        # Products
        text = re.sub(r'∏', r'\\prod', text)
        
        return text
    
    def _convert_matrices(self, text: str) -> str:
        """Convert matrix notation
        
        Args:
            text: Text with matrices
            
        Returns:
            Converted text
        """
        # Simple matrix detection
        matrix_pattern = r'\[\s*([^\]]+)\s*\]'
        
        def matrix_replacer(match):
            content = match.group(1)
            # Check if it looks like a matrix
            if ';' in content or '\n' in content:
                rows = content.split(';') if ';' in content else content.split('\n')
                matrix_content = ' \\\\ '.join(rows)
                return f'\\begin{{bmatrix}} {matrix_content} \\end{{bmatrix}}'
            return match.group(0)
        
        text = re.sub(matrix_pattern, matrix_replacer, text)
        
        return text
    
    def _convert_probability(self, text: str) -> str:
        """Convert probability notation
        
        Args:
            text: Text with probability notation
            
        Returns:
            Converted text
        """
        # P(A), P(A|B), etc.
        text = re.sub(r'P\s*\(([^)]+)\)', r'P(\1)', text)
        text = re.sub(r'P\s*\(([^|]+)\s*\|\s*([^)]+)\)', r'P(\1 \\mid \2)', text)
        
        # Expectation
        text = re.sub(r'E\s*\[([^\]]+)\]', r'\\mathbb{E}[\1]', text)
        
        # Variance
        text = re.sub(r'Var\s*\(([^)]+)\)', r'\\text{Var}(\1)', text)
        
        # Combinations and permutations
        text = re.sub(r'C\s*\(\s*([a-zA-Z0-9]+)\s*,\s*([a-zA-Z0-9]+)\s*\)',
                     r'\\binom{\1}{\2}', text)
        text = re.sub(r'nCr', r'\\binom{n}{r}', text)
        text = re.sub(r'nPr', r'P_n^r', text)
        
        return text
    
    def _convert_special_characters(self, text: str) -> str:
        """Convert special characters to LaTeX
        
        Args:
            text: Text with special characters
            
        Returns:
            Converted text
        """
        # Greek letters and symbols
        for symbol, latex in MATH_SYMBOLS.items():
            text = text.replace(symbol, latex)
        
        # LaTeX special characters that need escaping
        special_chars = {
            '%': r'\%',
            '&': r'\&',
            '#': r'\#',
            '_': r'\_',  # except in math mode
            '{': r'\{',
            '}': r'\}',
        }
        
        # Context-aware replacement would go here
        # For now, simple replacement in non-math contexts
        
        return text
    
    def _apply_math_mode(self, text: str, mode: str) -> str:
        """Apply appropriate math mode delimiters
        
        Args:
            text: Math text
            mode: Math mode type
            
        Returns:
            Text with delimiters
        """
        if mode in LATEX_DELIMITERS:
            start, end = LATEX_DELIMITERS[mode]
            
            # Check if already has delimiters
            if not text.startswith(start):
                text = f"{start}{text}{end}"
        
        return text
    
    def _format_for_document(self, text: str) -> str:
        """Format text for LaTeX document
        
        Args:
            text: LaTeX text
            
        Returns:
            Formatted text
        """
        # Restore protected LaTeX commands
        if hasattr(self, '_protected_commands'):
            for i, cmd in enumerate(self._protected_commands):
                placeholder = f"__LATEX_CMD_{i}__"
                text = text.replace(placeholder, cmd)
        
        # Ensure proper line breaks
        text = text.replace('\n\n', '\n\\medskip\n')
        
        return text
    
    def convert_question(self, question: Dict) -> str:
        """Convert a question to LaTeX format
        
        Args:
            question: Question dictionary
            
        Returns:
            LaTeX formatted question
        """
        latex_parts = []
        
        # Add question number if present
        if question.get('number'):
            latex_parts.append(f"\\textbf{{Question {question['number']}}}")
            latex_parts.append("\\\\")
        
        # Convert question text
        text = question.get('text', '')
        converted_text = self.convert(text)
        latex_parts.append(converted_text)
        
        # Add any sub-parts
        if question.get('parts'):
            latex_parts.append("\\begin{enumerate}")
            for part in question['parts']:
                part_text = self.convert(part)
                latex_parts.append(f"\\item {part_text}")
            latex_parts.append("\\end{enumerate}")
        
        return '\n'.join(latex_parts)
    
    def create_document(self, questions: List[Dict], metadata: Dict = None) -> str:
        """Create complete LaTeX document
        
        Args:
            questions: List of questions
            metadata: Document metadata
            
        Returns:
            Complete LaTeX document
        """
        doc_parts = []
        
        # Document class and packages
        doc_parts.extend([
            "\\documentclass[12pt]{article}",
            "\\usepackage{amsmath}",
            "\\usepackage{amssymb}",
            "\\usepackage{amsthm}",
            "\\usepackage{enumitem}",
            "\\usepackage{geometry}",
            "\\geometry{a4paper, margin=1in}",
            "",
        ])
        
        # Title
        if metadata:
            doc_parts.append("\\title{" + metadata.get('title', 'RD Sharma Questions') + "}")
            doc_parts.append("\\author{Extracted by RD Sharma Extractor}")
            doc_parts.append("\\date{\\today}")
        
        # Begin document
        doc_parts.extend([
            "",
            "\\begin{document}",
            ""
        ])
        
        if metadata:
            doc_parts.append("\\maketitle")
            doc_parts.append("")
        
        # Add questions
        for i, question in enumerate(questions, 1):
            latex_question = self.convert_question(question)
            doc_parts.append(latex_question)
            doc_parts.append("")
            doc_parts.append("\\vspace{1em}")
            doc_parts.append("")
        
        # End document
        doc_parts.append("\\end{document}")
        
        return '\n'.join(doc_parts)