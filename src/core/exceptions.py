"""Custom exceptions for the application"""

class RDSharmaExtractorError(Exception):
    """Base exception for RD Sharma Extractor"""
    pass

class ExtractionError(RDSharmaExtractorError):
    """Error during extraction process"""
    pass

class ValidationError(RDSharmaExtractorError):
    """Error during validation"""
    pass

class PDFProcessingError(RDSharmaExtractorError):
    """Error processing PDF file"""
    pass

class OCRError(RDSharmaExtractorError):
    """Error during OCR processing"""
    pass

class LaTeXConversionError(RDSharmaExtractorError):
    """Error converting to LaTeX"""
    pass

class LLMError(RDSharmaExtractorError):
    """Error with LLM processing"""
    pass