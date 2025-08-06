"""Text preprocessing and cleaning"""

import re
import logging
from typing import List, Dict, Optional
import unicodedata

from ..core.constants import MATH_SYMBOLS

class TextProcessor:
    """Process and clean text for better extraction"""
    
    def __init__(self):
        """Initialize text processor"""
        self.logger = logging.getLogger(__name__)
    
    def preprocess(self, text: str) -> str:
        """Preprocess text for extraction
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # Standardize mathematical notation
        text = self._standardize_math_notation(text)
        
        # Remove artifacts
        text = self._remove_artifacts(text)
        
        # Fix spacing
        text = self._fix_spacing(text)
        
        return text
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors
        
        Args:
            text: Text with potential OCR errors
            
        Returns:
            Fixed text
        """
        # Common OCR substitutions
        ocr_fixes = {
            'l': '1',  # in numeric contexts
            'O': '0',  # in numeric contexts
            '|': 'l',  # in text contexts
            '—': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }
        
        # Context-aware replacements would go here
        # For now, simple replacements
        for wrong, right in ocr_fixes.items():
            # This is simplified - real implementation would be context-aware
            pass
        
        return text
    
    def _standardize_math_notation(self, text: str) -> str:
        """Standardize mathematical notation
        
        Args:
            text: Text with math notation
            
        Returns:
            Standardized text
        """
        # Replace unicode math symbols with LaTeX equivalents
        for symbol, latex in MATH_SYMBOLS.items():
            text = text.replace(symbol, f' {latex} ')
        
        # Fix fraction notation
        text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
        
        # Fix exponent notation
        text = re.sub(r'(\w)\^(\w)', r'\1^{\2}', text)
        text = re.sub(r'(\w)\^(\d+)', r'\1^{\2}', text)
        
        # Fix subscript notation
        text = re.sub(r'(\w)_(\w)', r'\1_{\2}', text)
        text = re.sub(r'(\w)_(\d+)', r'\1_{\2}', text)
        
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove common artifacts from extracted text
        
        Args:
            text: Text with artifacts
            
        Returns:
            Cleaned text
        """
        # Remove page numbers
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove headers/footers
        text = re.sub(r'RD\s+SHARMA.*?Class\s+\d+', '', text, flags=re.IGNORECASE)
        
        # Remove watermarks (common patterns)
        text = re.sub(r'SAMPLE|WATERMARK|CONFIDENTIAL', '', text, flags=re.IGNORECASE)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues
        
        Args:
            text: Text with spacing issues
            
        Returns:
            Fixed text
        """
        # Fix multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = re.sub(r'([.,;:!?])(\w)', r'\1 \2', text)
        
        # Fix spacing around brackets
        text = re.sub(r'\s+\)', ')', text)
        text = re.sub(r'\(\s+', '(', text)
        
        return text.strip()
    
    def segment_questions(self, text: str) -> List[str]:
        """Segment text into individual questions
        
        Args:
            text: Text containing multiple questions
            
        Returns:
            List of question segments
        """
        # Pattern for question starts
        question_pattern = r'(?:^|\n)(?:\d+\.|Q\d+|Question \d+|Example \d+|Illustration \d+)'
        
        # Find all question starts
        matches = list(re.finditer(question_pattern, text, re.MULTILINE))
        
        if not matches:
            return [text] if text.strip() else []
        
        segments = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            segment = text[start:end].strip()
            if segment:
                segments.append(segment)
        
        return segments
    
    def extract_math_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text
        
        Args:
            text: Text containing math
            
        Returns:
            List of math expressions
        """
        expressions = []
        
        # Inline math $...$
        inline_math = re.findall(r'\$([^$]+)\$', text)
        expressions.extend(inline_math)
        
        # Display math $$...$$
        display_math = re.findall(r'\$\$([^$]+)\$\$', text)
        expressions.extend(display_math)
        
        # LaTeX environments
        environments = ['equation', 'align', 'gather', 'matrix']
        for env in environments:
            pattern = rf'\\begin{{{env}}}(.*?)\\end{{{env}}}'
            env_matches = re.findall(pattern, text, re.DOTALL)
            expressions.extend(env_matches)
        
        return expressions
    
    def clean_for_llm(self, text: str) -> str:
        """Clean text for LLM processing
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text suitable for LLM
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper sentence endings
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        # Remove special characters that might confuse LLM
        text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}\/\\\^_+=#$%&*@~`"\']', '', text)
        
        return text.strip()