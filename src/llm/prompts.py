"""Prompt templates for LLM"""

from typing import List, Dict

class PromptTemplates:
    """Templates for various LLM prompts"""
    
    def get_question_extraction_prompt(self, text: str) -> str:
        """Get prompt for question extraction
        
        Args:
            text: Input text
            
        Returns:
            Formatted prompt
        """
        return f"""You are an expert at extracting mathematical questions from RD Sharma textbooks.

Given the following text from RD Sharma Class 12, extract ALL questions (including examples, illustrations, and exercises).

TEXT:
{text}

INSTRUCTIONS:
1. Extract ONLY questions, not theory or explanations
2. Include question numbers if present
3. Preserve all mathematical notation
4. Include sub-parts (a), (b), (c) etc. if present
5. Each question should be complete and self-contained

OUTPUT FORMAT:
Return a JSON array where each element has:
- "number": Question number (if present)
- "text": Complete question text
- "type": Type of question (exercise/example/illustration)
- "parts": Array of sub-parts if present

IMPORTANT: Return ONLY the JSON array, no additional text."""
    
    def get_latex_conversion_prompt(self, text: str) -> str:
        """Get prompt for LaTeX conversion
        
        Args:
            text: Mathematical text
            
        Returns:
            Formatted prompt
        """
        return f"""Convert the following mathematical question to proper LaTeX format.

QUESTION:
{text}

INSTRUCTIONS:
1. Use proper LaTeX commands for all mathematical symbols
2. Use \\frac{{}} for fractions
3. Use ^ for superscripts and _ for subscripts (with braces)
4. Use \\sqrt{{}} for square roots
5. Use \\int, \\sum, \\prod for integrals, sums, products
6. Use \\begin{{equation}} or $ for math mode
7. Preserve the structure and meaning exactly

OUTPUT:
Return ONLY the LaTeX formatted question. Do not include any explanation."""
    
    def get_question_type_prompt(self, text: str) -> str:
        """Get prompt for question type identification
        
        Args:
            text: Question text
            
        Returns:
            Formatted prompt
        """
        return f"""Identify the type of this mathematical question from RD Sharma.

QUESTION:
{text}

TYPES:
- illustration: Worked example with solution
- example: Example problem
- exercise: Practice exercise
- objective: Multiple choice question
- subjective: Descriptive answer question

Return ONLY the type name, nothing else."""
    
    def get_latex_validation_prompt(self, latex: str) -> str:
        """Get prompt for LaTeX validation
        
        Args:
            latex: LaTeX code
            
        Returns:
            Formatted prompt
        """
        return f"""Validate the following LaTeX code for mathematical correctness and syntax.

LATEX:
{latex}

Check for:
1. Balanced braces {{}}
2. Correct command syntax
3. Proper math mode delimiters
4. Valid LaTeX commands

Return a JSON with:
- "valid": true/false
- "errors": list of error descriptions (if any)
- "corrected": corrected LaTeX (if there are errors)"""
    
    def get_improvement_prompt(self, text: str, initial_questions: List[str]) -> str:
        """Get prompt for improving extraction
        
        Args:
            text: Original text
            initial_questions: Initially extracted questions
            
        Returns:
            Formatted prompt
        """
        questions_str = "\n".join([f"{i+1}. {q}" for i, q in enumerate(initial_questions)])
        
        return f"""Review and improve the extraction of questions from this RD Sharma text.

ORIGINAL TEXT:
{text}

INITIALLY EXTRACTED QUESTIONS:
{questions_str}

Please:
1. Check if any questions were missed
2. Verify question completeness
3. Ensure mathematical notation is preserved
4. Check question numbering

Return an improved JSON array of questions with the same format as before."""