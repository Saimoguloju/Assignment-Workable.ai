"""Validation for extracted questions and LaTeX"""

import re
import logging
from typing import Dict, List, Optional, Tuple

class Validator:
    """Validate extracted questions and LaTeX formatting"""
    
    def __init__(self):
        """Initialize validator"""
        self.logger = logging.getLogger(__name__)
    
    def validate_question(self, question: Dict) -> Tuple[bool, List[str]]:
        """Validate a question
        
        Args:
            question: Question dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not question.get('text'):
            errors.append("Question text is missing")
        
        # Check text length
        if question.get('text') and len(question['text']) < 10:
            errors.append("Question text is too short")
        
        # Check for question indicators
        if not self._has_question_indicator(question.get('text', '')):
            errors.append("Text doesn't appear to be a question")
        
        # Validate LaTeX if present
        if question.get('latex'):
            latex_errors = self.validate_latex(question['latex'])
            errors.extend(latex_errors)
        
        return len(errors) == 0, errors
    
    def _has_question_indicator(self, text: str) -> bool:
        """Check if text has question indicators
        
        Args:
            text: Question text
            
        Returns:
            True if has indicators
        """
        indicators = [
            '?',
            'find', 'calculate', 'prove', 'show',
            'determine', 'evaluate', 'solve', 'verify'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators)
    
    def validate_latex(self, latex: str) -> List[str]:
        """Validate LaTeX syntax
        
        Args:
            latex: LaTeX string
            
        Returns:
            List of errors
        """
        errors = []
        
        # Check balanced braces
        if not self._check_balanced_braces(latex):
            errors.append("Unbalanced braces in LaTeX")
        
        # Check balanced math delimiters
        if not self._check_balanced_delimiters(latex):
            errors.append("Unbalanced math delimiters")
        
        # Check for common LaTeX errors
        common_errors = self._check_common_latex_errors(latex)
        errors.extend(common_errors)
        
        # Check for valid commands
        invalid_commands = self._check_invalid_commands(latex)
        if invalid_commands:
            errors.append(f"Invalid LaTeX commands: {', '.join(invalid_commands)}")
        
        return errors
    
    def _check_balanced_braces(self, latex: str) -> bool:
        """Check if braces are balanced
        
        Args:
            latex: LaTeX string
            
        Returns:
            True if balanced
        """
        count = 0
        for char in latex:
            if char == '{':
                count += 1
            elif char == '}':
                count -= 1
            if count < 0:
                return False
        return count == 0
    
    def _check_balanced_delimiters(self, latex: str) -> bool:
        """Check if math delimiters are balanced
        
        Args:
            latex: LaTeX string
            
        Returns:
            True if balanced
        """
        # Check $ delimiters
        dollar_count = latex.count('$') - latex.count('\\$')
        if dollar_count % 2 != 0:
            return False
        
        # Check \[ \] delimiters
        if latex.count('\\[') != latex.count('\\]'):
            return False
        
        # Check \( \) delimiters
        if latex.count('\\(') != latex.count('\\)'):
            return False
        
        # Check environments
        environments = re.findall(r'\\begin\{([^}]+)\}', latex)
        for env in environments:
            if latex.count(f'\\begin{{{env}}}') != latex.count(f'\\end{{{env}}}'):
                return False
        
        return True
    
    def _check_common_latex_errors(self, latex: str) -> List[str]:
        """Check for common LaTeX errors
        
        Args:
            latex: LaTeX string
            
        Returns:
            List of errors
        """
        errors = []
        
        # Check for double subscripts/superscripts
        if re.search(r'_.*_', latex) or re.search(r'\^.*\^', latex):
            errors.append("Double subscripts or superscripts detected")
        
        # Check for missing braces after commands
        if re.search(r'\\(frac|sqrt|sum|int)\s+[^{]', latex):
            errors.append("Missing braces after command")
        
        # Check for invalid fraction syntax
        if re.search(r'\\frac[^{]', latex):
            errors.append("Invalid fraction syntax")
        
        return errors
    
    def _check_invalid_commands(self, latex: str) -> List[str]:
        """Check for invalid LaTeX commands
        
        Args:
            latex: LaTeX string
            
        Returns:
            List of invalid commands
        """
        valid_commands = {
            'frac', 'sqrt', 'sum', 'int', 'prod', 'lim',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'alpha', 'beta', 'gamma', 'delta', 'theta',
            'lambda', 'mu', 'sigma', 'phi', 'omega',
            'infty', 'partial', 'nabla', 'times', 'cdot',
            'leq', 'geq', 'neq', 'approx', 'equiv',
            'subseteq', 'supseteq', 'in', 'notin',
            'cup', 'cap', 'emptyset', 'forall', 'exists',
            'rightarrow', 'leftarrow', 'Rightarrow', 'Leftarrow',
            'text', 'textbf', 'textit', 'mathbf', 'mathit',
            'begin', 'end', 'left', 'right', 'big', 'Big',
            'binom', 'choose', 'pmatrix', 'bmatrix', 'vmatrix'
        }
        
        # Find all commands in the LaTeX
        commands = re.findall(r'\\([a-zA-Z]+)', latex)
        
        # Check for invalid commands
        invalid = [cmd for cmd in commands if cmd not in valid_commands]
        
        return invalid
    
    def validate_batch(self, questions: List[Dict]) -> Dict:
        """Validate a batch of questions
        
        Args:
            questions: List of questions
            
        Returns:
            Validation report
        """
        report = {
            'total': len(questions),
            'valid': 0,
            'invalid': 0,
            'errors': [],
            'warnings': []
        }
        
        for i, question in enumerate(questions):
            is_valid, errors = self.validate_question(question)
            
            if is_valid:
                report['valid'] += 1
            else:
                report['invalid'] += 1
                report['errors'].append({
                    'question_index': i,
                    'errors': errors
                })
        
        # Add warnings for common issues
        if report['invalid'] > report['total'] * 0.2:
            report['warnings'].append("More than 20% of questions failed validation")
        
        return report