"""Base extractor abstract class"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

class BaseExtractor(ABC):
    """Abstract base class for all extractors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the extractor
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def extract(self, source: Any) -> Any:
        """Extract content from source
        
        Args:
            source: Source to extract from
            
        Returns:
            Extracted content
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: Any) -> bool:
        """Validate if source is valid for extraction
        
        Args:
            source: Source to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def preprocess(self, source: Any) -> Any:
        """Preprocess source before extraction
        
        Args:
            source: Source to preprocess
            
        Returns:
            Preprocessed source
        """
        return source
    
    def postprocess(self, extracted: Any) -> Any:
        """Postprocess extracted content
        
        Args:
            extracted: Extracted content
            
        Returns:
            Postprocessed content
        """
        return extracted