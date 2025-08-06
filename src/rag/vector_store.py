"""Vector store for embeddings"""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
import chromadb
from chromadb.config import Settings

from ..core.config import get_config

class VectorStore:
    """Store and retrieve vectors using ChromaDB"""
    
    def __init__(self, collection_name: str = "rd_sharma_questions"):
        """Initialize vector store
        
        Args:
            collection_name: Name of the collection
        """
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.collection_name = collection_name
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.config.vector_store_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RD Sharma questions and solutions"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[np.ndarray],
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ):
        """Add documents to vector store
        
        Args:
            documents: List of document texts
            embeddings: List of embeddings
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        if metadatas is None:
            metadatas = [{}] * len(documents)
        
        # Convert numpy arrays to lists for ChromaDB
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
        
        self.logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        filter_dict: Dict = None
    ) -> List[Dict]:
        """Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            filter_dict: Metadata filters
            
        Returns:
            List of search results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0,
                'id': results['ids'][0][i] if results['ids'] else None
            })
        
        return formatted_results
    
    def delete_collection(self):
        """Delete the collection"""
        self.client.delete_collection(name=self.collection_name)
        self.logger.info(f"Deleted collection: {self.collection_name}")
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection
        
        Returns:
            Collection information
        """
        count = self.collection.count()
        
        return {
            'name': self.collection_name,
            'count': count,
            'metadata': self.collection.metadata
        }
    
    def update_document(self, doc_id: str, document: str, embedding: np.ndarray, metadata: Dict = None):
        """Update a document in the store
        
        Args:
            doc_id: Document ID
            document: Document text
            embedding: Document embedding
            metadata: Document metadata
        """
        self.collection.update(
            ids=[doc_id],
            documents=[document],
            embeddings=[embedding.tolist()],
            metadatas=[metadata] if metadata else None
        )