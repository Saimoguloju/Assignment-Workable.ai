"""RD Sharma Question Extractor Package"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.config import Config
from .rag.rag_pipeline import RAGPipeline

__all__ = ["Config", "RAGPipeline"]