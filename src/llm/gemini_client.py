"""Google Gemini API client"""

import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_config
from ..core.exceptions import LLMError
from .prompts import PromptTemplates
from .response_parser import ResponseParser

class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Configure Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize helpers
        self.prompts = PromptTemplates()
        self.parser = ResponseParser()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_response(self, prompt: str) -> str:
        """Generate response from Gemini
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise LLMError(f"Failed to generate response: {e}")
    
    def extract_questions(self, text: str) -> List[Dict]:
        """Extract questions from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted questions
        """
        prompt = self.prompts.get_question_extraction_prompt(text)
        response = self.generate_response(prompt)
        
        # Parse response
        questions = self.parser.parse_questions(response)
        
        return questions
    
    def convert_to_latex(self, text: str) -> str:
        """Convert mathematical text to LaTeX
        
        Args:
            text: Mathematical text
            
        Returns:
            LaTeX formatted text
        """
        prompt = self.prompts.get_latex_conversion_prompt(text)
        response = self.generate_response(prompt)
        
        # Parse LaTeX from response
        latex = self.parser.parse_latex(response)
        
        return latex
    
    def identify_question_type(self, text: str) -> str:
        """Identify type of question
        
        Args:
            text: Question text
            
        Returns:
            Question type
        """
        prompt = self.prompts.get_question_type_prompt(text)
        response = self.generate_response(prompt)
        
        # Parse question type
        question_type = self.parser.parse_question_type(response)
        
        return question_type
    
    def validate_latex(self, latex: str) -> Dict:
        """Validate LaTeX syntax
        
        Args:
            latex: LaTeX code
            
        Returns:
            Validation result
        """
        prompt = self.prompts.get_latex_validation_prompt(latex)
        response = self.generate_response(prompt)
        
        # Parse validation result
        validation = self.parser.parse_validation(response)
        
        return validation
    
    def improve_question_extraction(self, text: str, initial_questions: List[str]) -> List[Dict]:
        """Improve question extraction using feedback
        
        Args:
            text: Original text
            initial_questions: Initially extracted questions
            
        Returns:
            Improved list of questions
        """
        prompt = self.prompts.get_improvement_prompt(text, initial_questions)
        response = self.generate_response(prompt)
        
        # Parse improved questions
        improved_questions = self.parser.parse_questions(response)
        
        return improved_questions
    
    def batch_process(self, texts: List[str], operation: str) -> List:
        """Process multiple texts
        
        Args:
            texts: List of texts
            operation: Operation to perform
            
        Returns:
            List of results
        """
        results = []
        
        for text in texts:
            try:
                if operation == "extract":
                    result = self.extract_questions(text)
                elif operation == "latex":
                    result = self.convert_to_latex(text)
                elif operation == "type":
                    result = self.identify_question_type(text)
                else:
                    result = None
                
                results.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to process text: {e}")
                results.append(None)
        
        return results