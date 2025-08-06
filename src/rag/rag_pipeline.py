"""RAG pipeline orchestration"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .retriever import Retriever
from ..extractors.pdf_extractor import PDFExtractor
from ..extractors.question_extractor import QuestionExtractor
from ..processors.text_processor import TextProcessor
from ..processors.latex_converter import LaTeXConverter
from ..llm.gemini_client import GeminiClient
from ..core.config import get_config

class RAGPipeline:
    """Complete RAG pipeline for question extraction"""
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pdf_extractor = PDFExtractor()
        self.question_extractor = QuestionExtractor()
        self.text_processor = TextProcessor()
        self.latex_converter = LaTeXConverter()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.retriever = Retriever(self.vector_store)
        self.llm_client = GeminiClient()
    
    def process_pdf(
        self,
        pdf_path: Path,
        chapter: int,
        topic: str
    ) -> Dict:
        """Process PDF and extract questions
        
        Args:
            pdf_path: Path to PDF file
            chapter: Chapter number
            topic: Topic identifier
            
        Returns:
            Extraction results
        """
        self.logger.info(f"Processing PDF: {pdf_path}, Chapter: {chapter}, Topic: {topic}")
        
        # Extract content from PDF
        pdf_content = self.pdf_extractor.extract_chapter_topic(
            pdf_path, chapter, topic
        )
        
        # Process extracted pages
        all_questions = []
        
        for page in tqdm(pdf_content['pages'], desc="Processing pages"):
            # Preprocess text
            processed_text = self.text_processor.preprocess(page['text'])
            
            # Extract questions
            questions = self.question_extractor.extract(processed_text)
            
            # Add page number to questions
            for q in questions:
                q.page_number = page['page_number']
            
            all_questions.extend(questions)
        
        # Convert to LaTeX using LLM
        latex_questions = self._convert_questions_to_latex(all_questions)
        
        # Index questions for future retrieval
        self._index_questions(latex_questions, chapter, topic)
        
        return {
            'chapter': chapter,
            'topic': topic,
            'questions': latex_questions,
            'total_questions': len(latex_questions),
            'metadata': pdf_content['metadata']
        }
    
    def _convert_questions_to_latex(self, questions: List) -> List[Dict]:
        """Convert questions to LaTeX format using LLM
        
        Args:
            questions: List of Question objects
            
        Returns:
            List of LaTeX formatted questions
        """
        latex_questions = []
        
        for question in tqdm(questions, desc="Converting to LaTeX"):
            # Use LLM for accurate conversion
            latex_text = self.llm_client.convert_to_latex(question.text)
            
            # Fallback to rule-based converter if LLM fails
            if not latex_text:
                latex_text = self.latex_converter.convert(question.text)
            
            latex_questions.append({
                'original_text': question.text,
                'latex': latex_text,
                'question_type': question.question_type.value,
                'number': question.number,
                'page_number': question.page_number,
                'confidence': question.confidence
            })
        
        return latex_questions
    
    def _index_questions(self, questions: List[Dict], chapter: int, topic: str):
        """Index questions for retrieval
        
        Args:
            questions: List of questions
            chapter: Chapter number
            topic: Topic identifier
        """
        documents = []
        metadatas = []
        
        for i, question in enumerate(questions):
            # Create document text
            doc_text = f"{question['original_text']}\n\nLaTeX: {question['latex']}"
            documents.append(doc_text)
            
            # Create metadata
            metadata = {
                'chapter': chapter,
                'topic': topic,
                'question_type': question['question_type'],
                'page_number': question['page_number'],
                'question_number': question['number'],
                'confidence': question['confidence']
            }
            metadatas.append(metadata)
        
        # Add to index
        self.retriever.add_documents_to_index(documents, metadatas)
        
        self.logger.info(f"Indexed {len(questions)} questions")
    
    def search_questions(
        self,
        query: str,
        chapter: Optional[int] = None,
        topic: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar questions
        
        Args:
            query: Search query
            chapter: Filter by chapter
            topic: Filter by topic
            n_results: Number of results
            
        Returns:
            Search results
        """
        # Build filter
        filter_dict = {}
        if chapter:
            filter_dict['chapter'] = chapter
        if topic:
            filter_dict['topic'] = topic
        
        # Retrieve results
        results = self.retriever.retrieve(
            query=query,
            n_results=n_results,
            filter_dict=filter_dict if filter_dict else None
        )
        
        return results
    
    def process_batch(
        self,
        pdf_path: Path,
        chapters_topics: List[Tuple[int, str]]
    ) -> List[Dict]:
        """Process multiple chapters/topics
        
        Args:
            pdf_path: Path to PDF
            chapters_topics: List of (chapter, topic) tuples
            
        Returns:
            List of extraction results
        """
        results = []
        
        for chapter, topic in chapters_topics:
            try:
                result = self.process_pdf(pdf_path, chapter, topic)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {chapter}.{topic}: {e}")
                results.append({
                    'chapter': chapter,
                    'topic': topic,
                    'error': str(e)
                })
        
        return results