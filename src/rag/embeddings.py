"""Generate embeddings for text chunks"""

import logging
from typing import List, Dict, Optional
import numpy as np
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_config
from ..core.exceptions import LLMError

class EmbeddingGenerator:
    """Generate embeddings using Gemini"""
    
    def __init__(self):
        """Initialize embedding generator"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Configure Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        self.model = self.config.embedding_model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'])
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise LLMError(f"Failed to generate embedding: {e}")
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts
        
        Args:
            texts: List of texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.warning(f"Failed to embed text: {e}")
                # Use zero vector as fallback
                embeddings.append(np.zeros(768))
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for query
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"
            )
            return np.array(result['embedding'])
        except Exception as e:
            self.logger.error(f"Error generating query embedding: {e}")
            raise LLMError(f"Failed to generate query embedding: {e}")