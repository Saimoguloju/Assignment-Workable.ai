"""Question identification and extraction"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .base_extractor import BaseExtractor
from ..core.constants import QUESTION_PATTERNS, QuestionType
from ..core.exceptions import ExtractionError

@dataclass
class Question:
    """Represents an extracted question"""
    text: str
    question_type: QuestionType
    number: Optional[str] = None
    page_number: Optional[int] = None
    confidence: float = 1.0
    metadata: Dict = None

class QuestionExtractor(BaseExtractor):
    """Extract and identify questions from text"""
    
    def __init__(self):
        """Initialize question extractor"""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.question_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for question detection
        
        Returns:
            List of compiled patterns
        """
        return [re.compile(pattern, re.MULTILINE) for pattern in QUESTION_PATTERNS]
    
    def validate_source(self, source: str) -> bool:
        """Validate text source
        
        Args:
            source: Text to validate
            
        Returns:
            True if valid
        """
        return isinstance(source, str) and len(source) > 0
    
    def extract(self, source: str) -> List[Question]:
        """Extract questions from text
        
        Args:
            source: Text containing questions
            
        Returns:
            List of extracted questions
        """
        if not self.validate_source(source):
            raise ExtractionError("Invalid source text")
        
        questions = []
        
        # Split text into potential question blocks
        blocks = self._split_into_blocks(source)
        
        for block in blocks:
            if self._is_question_block(block):
                question = self._extract_question(block)
                if question:
                    questions.append(question)
        
        return self.postprocess(questions)
    
    def _split_into_blocks(self, text: str) -> List[str]:
        """Split text into potential question blocks
        
        Args:
            text: Input text
            
        Returns:
            List of text blocks
        """
        # Split by double newlines or question patterns
        blocks = []
        current_block = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line starts a new question
            if self._is_question_start(line):
                if current_block:
                    blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _is_question_start(self, line: str) -> bool:
        """Check if line starts a question
        
        Args:
            line: Text line
            
        Returns:
            True if question start
        """
        line = line.strip()
        
        for pattern in self.question_patterns:
            if pattern.match(line):
                return True
        
        # Additional heuristics
        if re.match(r'^\([a-z]\)', line):  # (a), (b), etc.
            return True
        if re.match(r'^[IVX]+\.', line):  # Roman numerals
            return True
        
        return False
    
    def _is_question_block(self, block: str) -> bool:
        """Determine if block contains a question
        
        Args:
            block: Text block
            
        Returns:
            True if contains question
        """
        # Check for question indicators
        question_indicators = [
            '?',  # Question mark
            'Find',
            'Calculate',
            'Prove',
            'Show that',
            'Determine',
            'Evaluate',
            'Solve',
            'If',
            'When',
            'What',
            'Which',
            'How',
            'Why',
            'Verify',
            'Derive',
            'Explain',
            'State',
            'Define',
            'Given',
        ]
        
        block_lower = block.lower()
        
        for indicator in question_indicators:
            if indicator.lower() in block_lower:
                return True
        
        # Check for mathematical content
        if self._contains_math(block):
            # Even without explicit question words, math content might be a problem
            return True
        
        return False
    
    def _contains_math(self, text: str) -> bool:
        """Check if text contains mathematical content
        
        Args:
            text: Text to check
            
        Returns:
            True if contains math
        """
        math_indicators = [
            r'\d+[\+\-\*/]\d+',  # Basic operations
            r'[xy]=',  # Equations
            r'\\[a-zA-Z]+',  # LaTeX commands
            r'[∫∑∏√]',  # Math symbols
            r'\^',  # Exponents
            r'_{',  # Subscripts
            r'\\frac',  # Fractions
            r'\\sqrt',  # Square roots
            r'P\([^)]+\)',  # Probability notation
        ]
        
        for pattern in math_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _extract_question(self, block: str) -> Optional[Question]:
        """Extract question from block
        
        Args:
            block: Text block
            
        Returns:
            Question object or None
        """
        # Clean the block
        cleaned = self._clean_text(block)
        
        if not cleaned:
            return None
        
        # Determine question type
        question_type = self._determine_question_type(block)
        
        # Extract question number if present
        number = self._extract_question_number(block)
        
        return Question(
            text=cleaned,
            question_type=question_type,
            number=number,
            confidence=self._calculate_confidence(block)
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean text for question extraction
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers, headers, footers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'RD SHARMA.*?Class.*?\d+', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _determine_question_type(self, text: str) -> QuestionType:
        """Determine type of question
        
        Args:
            text: Question text
            
        Returns:
            Question type
        """
        text_lower = text.lower()
        
        if 'illustration' in text_lower:
            return QuestionType.ILLUSTRATION
        elif 'example' in text_lower:
            return QuestionType.EXAMPLE
        elif 'exercise' in text_lower:
            return QuestionType.EXERCISE
        elif 'objective' in text_lower:
            return QuestionType.OBJECTIVE
        else:
            return QuestionType.PRACTICE
    
    def _extract_question_number(self, text: str) -> Optional[str]:
        """Extract question number
        
        Args:
            text: Question text
            
        Returns:
            Question number or None
        """
        # Try different number patterns
        patterns = [
            r'^(\d+)\.',
            r'^Q(\d+)',
            r'^Question (\d+)',
            r'^\(([a-z])\)',
            r'^([IVX]+)\.',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for question extraction
        
        Args:
            text: Question text
            
        Returns:
            Confidence score (0-1)
        """
        score = 0.5  # Base score
        
        # Increase score for question indicators
        if '?' in text:
            score += 0.2
        
        if self._contains_math(text):
            score += 0.1
        
        if self._extract_question_number(text):
            score += 0.1
        
        # Check for question keywords
        question_keywords = ['find', 'prove', 'show', 'calculate', 'determine']
        if any(kw in text.lower() for kw in question_keywords):
            score += 0.1
        
        return min(score, 1.0)
    
    def extract_from_pages(self, pages: List[Dict]) -> List[Question]:
        """Extract questions from multiple pages
        
        Args:
            pages: List of page dictionaries
            
        Returns:
            List of questions
        """
        all_questions = []
        
        for page in pages:
            page_text = page.get("text", "")
            page_number = page.get("page_number")
            
            questions = self.extract(page_text)
            
            # Add page number to questions
            for question in questions:
                question.page_number = page_number
            
            all_questions.extend(questions)
        
        return all_questions