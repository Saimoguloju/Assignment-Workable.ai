"""Retrieval logic for RAG pipeline"""

import logging
from typing import List, Dict, Optional
import numpy as np

from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore

class Retriever:
    """Retrieve relevant documents for queries"""
    
    def __init__(self, vector_store: VectorStore = None):
        """Initialize retriever
        
        Args:
            vector_store: Vector store instance
        """
        self.logger = logging.getLogger(__name__)
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = vector_store or VectorStore()
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Dict = None
    ) -> List[Dict]:
        """Retrieve relevant documents for query
        
        Args:
            query: Query text
            n_results: Number of results
            filter_dict: Metadata filters
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filter_dict
        )
        
        # Rerank results if needed
        results = self._rerank_results(query, results)
        
        return results
    
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank search results
        
        Args:
            query: Original query
            results: Search results
            
        Returns:
            Reranked results
        """
        # Simple reranking based on keyword matching
        query_words = set(query.lower().split())
        
        for result in results:
            doc_words = set(result['document'].lower().split())
            overlap = len(query_words & doc_words)
            result['keyword_score'] = overlap / len(query_words) if query_words else 0
        
        # Combine vector similarity and keyword score
        for result in results:
            vector_score = 1 / (1 + result['distance'])  # Convert distance to similarity
            keyword_score = result['keyword_score']
            result['combined_score'] = 0.7 * vector_score + 0.3 * keyword_score
        
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return results
    
    def add_documents_to_index(
        self,
        documents: List[str],
        metadatas: List[Dict] = None
    ):
        """Add documents to the index
        
        Args:
            documents: List of documents
            metadatas: List of metadata
        """
        # Generate embeddings
        embeddings = self.embedding_generator.generate_batch_embeddings(documents)
        
        # Add to vector store
        self.vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        self.logger.info(f"Added {len(documents)} documents to index")