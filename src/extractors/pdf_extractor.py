"""PDF text extraction module"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF
import pdfplumber
from PyPDF2 import PdfReader

from .base_extractor import BaseExtractor
from ..core.exceptions import PDFProcessingError
from ..core.config import get_config

class PDFExtractor(BaseExtractor):
    """Extract text from PDF files"""
    
    def __init__(self, use_ocr: bool = False):
        """Initialize PDF extractor
        
        Args:
            use_ocr: Whether to use OCR for scanned pages
        """
        super().__init__()
        self.config = get_config()
        self.use_ocr = use_ocr or self.config.ocr_enabled
        self.logger = logging.getLogger(__name__)
    
    def validate_source(self, source: Path) -> bool:
        """Validate PDF file
        
        Args:
            source: Path to PDF file
            
        Returns:
            True if valid PDF
        """
        if not isinstance(source, (str, Path)):
            return False
        
        source = Path(source)
        
        if not source.exists():
            self.logger.error(f"PDF file does not exist: {source}")
            return False
        
        if not source.suffix.lower() == '.pdf':
            self.logger.error(f"Not a PDF file: {source}")
            return False
        
        # Check file size
        if source.stat().st_size > self.config.max_pdf_size_bytes:
            self.logger.error(f"PDF file too large: {source}")
            return False
        
        return True
    
    def extract(self, source: Path) -> Dict[str, any]:
        """Extract text from PDF
        
        Args:
            source: Path to PDF file
            
        Returns:
            Dictionary with extracted content
        """
        if not self.validate_source(source):
            raise PDFProcessingError(f"Invalid PDF source: {source}")
        
        source = Path(source)
        extracted_data = {
            "filename": source.name,
            "pages": [],
            "metadata": {},
            "total_pages": 0
        }
        
        try:
            # Try multiple extraction methods
            text_content = self._extract_with_pymupdf(source)
            
            if not text_content or self._is_scanned_pdf(text_content):
                self.logger.info("Detected scanned PDF, trying pdfplumber...")
                text_content = self._extract_with_pdfplumber(source)
            
            if not text_content or len(text_content) < 100:
                self.logger.info("Minimal text extracted, PDF might be scanned")
                if self.use_ocr:
                    from .ocr_extractor import OCRExtractor
                    ocr = OCRExtractor()
                    text_content = ocr.extract(source)
            
            extracted_data.update(text_content)
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF: {e}")
            raise PDFProcessingError(f"Failed to extract PDF: {e}")
        
        return self.postprocess(extracted_data)
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> Dict:
        """Extract using PyMuPDF
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Extracted content
        """
        doc = fitz.open(pdf_path)
        pages = []
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            pages.append({
                "page_number": page_num,
                "text": text,
                "bbox": page.rect,
                "images": len(page.get_images()),
                "tables": self._extract_tables_from_page(page)
            })
        
        metadata = doc.metadata
        doc.close()
        
        return {
            "pages": pages,
            "metadata": metadata,
            "total_pages": len(pages)
        }
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> Dict:
        """Extract using pdfplumber
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Extracted content
        """
        pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []
                
                pages.append({
                    "page_number": page_num,
                    "text": text,
                    "tables": tables,
                    "bbox": page.bbox
                })
            
            metadata = pdf.metadata
        
        return {
            "pages": pages,
            "metadata": metadata,
            "total_pages": len(pages)
        }
    
    def _extract_tables_from_page(self, page) -> List:
        """Extract tables from a page
        
        Args:
            page: Page object
            
        Returns:
            List of extracted tables
        """
        # Simplified table extraction
        tables = []
        # Implementation depends on specific needs
        return tables
    
    def _is_scanned_pdf(self, content: Dict) -> bool:
        """Check if PDF is scanned (image-based)
        
        Args:
            content: Extracted content
            
        Returns:
            True if scanned PDF
        """
        if not content.get("pages"):
            return True
        
        total_text = sum(len(p.get("text", "")) for p in content["pages"])
        total_images = sum(p.get("images", 0) for p in content["pages"])
        
        # Heuristic: if very little text but many images, likely scanned
        if total_text < 500 and total_images > len(content["pages"]):
            return True
        
        return False
    
    def extract_chapter_topic(self, pdf_path: Path, chapter: int, topic: str) -> Dict:
        """Extract specific chapter and topic
        
        Args:
            pdf_path: Path to PDF
            chapter: Chapter number
            topic: Topic identifier (e.g., "30.3")
            
        Returns:
            Extracted content for the topic
        """
        full_content = self.extract(pdf_path)
        
        # Find pages containing the topic
        topic_pages = []
        topic_started = False
        next_topic = self._get_next_topic(chapter, topic)
        
        for page in full_content["pages"]:
            text = page["text"]
            
            # Check if topic starts in this page
            if topic in text and not topic_started:
                topic_started = True
            
            # If topic has started, add page
            if topic_started:
                topic_pages.append(page)
                
                # Check if next topic starts (end of current topic)
                if next_topic and next_topic in text:
                    break
        
        return {
            "chapter": chapter,
            "topic": topic,
            "pages": topic_pages,
            "metadata": full_content["metadata"]
        }
    
    def _get_next_topic(self, chapter: int, current_topic: str) -> Optional[str]:
        """Get the next topic in sequence
        
        Args:
            chapter: Chapter number
            current_topic: Current topic
            
        Returns:
            Next topic identifier or None
        """
        from ..core.constants import CHAPTER_TOPICS
        
        if chapter not in CHAPTER_TOPICS:
            return None
        
        topics = list(CHAPTER_TOPICS[chapter]["topics"].keys())
        
        try:
            current_index = topics.index(current_topic)
            if current_index < len(topics) - 1:
                return topics[current_index + 1]
        except ValueError:
            pass
        
        return None