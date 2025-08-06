"""File handling utilities"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

class FileHandler:
    """Handle various file operations"""
    
    @staticmethod
    def save_json(data: Any, filepath: Path):
        """Save data as JSON
        
        Args:
            data: Data to save
            filepath: Output filepath
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_json(filepath: Path) -> Any:
        """Load JSON file
        
        Args:
            filepath: Input filepath
            
        Returns:
            Loaded data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_latex(content: str, filepath: Path):
        """Save LaTeX content
        
        Args:
            content: LaTeX content
            filepath: Output filepath
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def save_markdown(content: str, filepath: Path):
        """Save Markdown content
        
        Args:
            content: Markdown content
            filepath: Output filepath
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def save_pickle(obj: Any, filepath: Path):
        """Save object as pickle
        
        Args:
            obj: Object to save
            filepath: Output filepath
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
    
    @staticmethod
    def load_pickle(filepath: Path) -> Any:
        """Load pickle file
        
        Args:
            filepath: Input filepath
            
        Returns:
            Loaded object
        """
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    @staticmethod
    def save_csv(data: List[Dict], filepath: Path):
        """Save data as CSV
        
        Args:
            data: List of dictionaries
            filepath: Output filepath
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
    
    @staticmethod
    def load_csv(filepath: Path) -> pd.DataFrame:
        """Load CSV file
        
        Args:
            filepath: Input filepath
            
        Returns:
            DataFrame
        """
        return pd.read_csv(filepath, encoding='utf-8')