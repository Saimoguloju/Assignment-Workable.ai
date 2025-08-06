"""Helper functions"""

import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime

def generate_id(text: str) -> str:
    """Generate unique ID from text
    
    Args:
        text: Input text
        
    Returns:
        Unique ID
    """
    return hashlib.md5(text.encode()).hexdigest()[:12]

def timestamp() -> str:
    """Get current timestamp
    
    Returns:
        ISO format timestamp
    """
    return datetime.now().isoformat()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Chunk text with overlap
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def clean_filename(filename: str) -> str:
    """Clean filename for safe saving
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename

def format_question_output(question: Dict) -> str:
    """Format question for display
    
    Args:
        question: Question dictionary
        
    Returns:
        Formatted string
    """
    output = []
    
    if question.get('number'):
        output.append(f"Question {question['number']}:")
    
    output.append(question.get('latex', question.get('text', '')))
    
    if question.get('parts'):
        for i, part in enumerate(question['parts']):
            output.append(f"  ({chr(97+i)}) {part}")
    
    return '\n'.join(output)