"""OCR extraction for scanned PDFs"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import pytesseract
from PIL import Image
import pdf2image
import cv2
import numpy as np

from .base_extractor import BaseExtractor
from ..core.exceptions import OCRError
from ..core.config import get_config

class OCRExtractor(BaseExtractor):
    """Extract text from images using OCR"""
    
    def __init__(self):
        """Initialize OCR extractor"""
        super().__init__()
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Configure tesseract
        self.tesseract_config = r'--oem 3 --psm 6'
        self.language = self.config.ocr_language
    
    def validate_source(self, source: Path) -> bool:
        """Validate source for OCR
        
        Args:
            source: Path to file
            
        Returns:
            True if valid
        """
        source = Path(source)
        
        if not source.exists():
            return False
        
        # Check if it's a PDF or image
        valid_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        if source.suffix.lower() not in valid_extensions:
            return False
        
        return True
    
    def extract(self, source: Path) -> Dict:
        """Extract text using OCR
        
        Args:
            source: Path to file
            
        Returns:
            Extracted text content
        """
        if not self.validate_source(source):
            raise OCRError(f"Invalid source for OCR: {source}")
        
        source = Path(source)
        
        try:
            if source.suffix.lower() == '.pdf':
                return self._extract_from_pdf(source)
            else:
                return self._extract_from_image(source)
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            raise OCRError(f"OCR extraction failed: {e}")
    
    def _extract_from_pdf(self, pdf_path: Path) -> Dict:
        """Extract text from PDF using OCR
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Extracted content
        """
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path, dpi=300)
        
        pages = []
        for i, image in enumerate(images, 1):
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=self.tesseract_config
            )
            
            # Also extract with layout preservation
            hocr = pytesseract.image_to_pdf_or_hocr(
                processed_image,
                lang=self.language,
                extension='hocr'
            )
            
            pages.append({
                "page_number": i,
                "text": text,
                "hocr": hocr,
                "confidence": self._get_confidence(processed_image)
            })
            
            self.logger.info(f"OCR completed for page {i}/{len(images)}")
        
        return {
            "pages": pages,
            "total_pages": len(pages),
            "extraction_method": "OCR"
        }
    
    def _extract_from_image(self, image_path: Path) -> Dict:
        """Extract text from image
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text
        """
        image = Image.open(image_path)
        processed_image = self._preprocess_image(image)
        
        text = pytesseract.image_to_string(
            processed_image,
            lang=self.language,
            config=self.tesseract_config
        )
        
        return {
            "text": text,
            "source": str(image_path),
            "extraction_method": "OCR"
        }
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed image array
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Deskew
        deskewed = self._deskew(denoised)
        
        return deskewed
    
    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Deskew image
        
        Args:
            image: Image array
            
        Returns:
            Deskewed image
        """
        coords = np.column_stack(np.where(image > 0))
        
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def _get_confidence(self, image: np.ndarray) -> float:
        """Get OCR confidence score
        
        Args:
            image: Image array
            
        Returns:
            Confidence score
        """
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT
        )
        
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        
        if confidences:
            return sum(confidences) / len(confidences)
        
        return 0.0
    
    def extract_math_regions(self, image: Image.Image) -> List[Dict]:
        """Extract mathematical regions from image
        
        Args:
            image: PIL Image
            
        Returns:
            List of math regions
        """
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Find contours that might be mathematical expressions
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        math_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on size and aspect ratio
            if w > 30 and h > 20:
                region = img_array[y:y+h, x:x+w]
                math_regions.append({
                    "bbox": (x, y, w, h),
                    "image": region
                })
        
        return math_regions