"""Parse LLM responses"""

import json
import re
import logging
from typing import Dict, List, Optional, Any

class ResponseParser:
    """Parse responses from LLM"""
    
    def __init__(self):
        """Initialize response parser"""
        self.logger = logging.getLogger(__name__)
    
    def parse_questions(self, response: str) -> List[Dict]:
        """Parse questions from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            List of parsed questions
        """
        try:
            # Try to parse as JSON
            questions = json.loads(response)
            
            if isinstance(questions, list):
                return questions
            else:
                self.logger.warning("Response is not a list")
                return []
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            
            if json_match:
                try:
                    questions = json.loads(json_match.group())
                    return questions
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Parse as text
            return self._parse_questions_from_text(response)
    
    def _parse_questions_from_text(self, text: str) -> List[Dict]:
        """Parse questions from plain text
        
        Args:
            text: Plain text
            
        Returns:
            List of questions
        """
        questions = []
        
        # Split by question numbers
        parts = re.split(r'\n(?=\d+\.|\([a-z]\))', text)
        
        for part in parts:
            part = part.strip()
            if part:
                # Extract number
                number_match = re.match(r'^(\d+)\.\s*(.+)', part)
                
                if number_match:
                    questions.append({
                        'number': number_match.group(1),
                        'text': number_match.group(2),
                        'type': 'unknown'
                    })
                else:
                    questions.append({
                        'text': part,
                        'type': 'unknown'
                    })
        
        return questions
    
    def parse_latex(self, response: str) -> str:
        """Parse LaTeX from response
        
        Args:
            response: LLM response
            
        Returns:
            LaTeX string
        """
        # Remove any markdown code blocks
        response = re.sub(r'```latex\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        
        # Remove any explanatory text before/after
        lines = response.split('\n')
        latex_lines = []
        
        for line in lines:
            # Skip lines that look like explanations
            if not any(phrase in line.lower() for phrase in 
                      ['here is', 'this is', 'the latex', 'converted']):
                latex_lines.append(line)
        
        return '\n'.join(latex_lines).strip()
    
    def parse_question_type(self, response: str) -> str:
        """Parse question type from response
        
        Args:
            response: LLM response
            
        Returns:
            Question type
        """
        response = response.strip().lower()
        
        valid_types = ['illustration', 'example', 'exercise', 'objective', 'subjective']
        
        for q_type in valid_types:
            if q_type in response:
                return q_type
        
        return 'unknown'
    
    def parse_validation(self, response: str) -> Dict:
        """Parse validation result
        
        Args:
            response: LLM response
            
        Returns:
            Validation result
        """
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            return {
                'valid': 'error' not in response.lower(),
                'errors': [],
                'corrected': None
            }