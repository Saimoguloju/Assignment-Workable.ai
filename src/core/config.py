"""Configuration management for the application"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Application configuration"""
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Application Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cache_enabled: bool = Field(True, env="CACHE_ENABLED")
    cache_dir: Path = Field(Path("./data/cache"), env="CACHE_DIR")
    
    # Vector Store Settings
    vector_store_path: Path = Field(Path("./data/vectorstore"), env="VECTOR_STORE_PATH")
    embedding_model: str = Field("models/embedding-001", env="EMBEDDING_MODEL")
    
    # Output Settings
    output_dir: Path = Field(Path("./output"), env="OUTPUT_DIR")
    default_export_format: str = Field("latex", env="DEFAULT_EXPORT_FORMAT")
    
    # PDF Settings
    max_pdf_size_mb: int = Field(100, env="MAX_PDF_SIZE_MB")
    ocr_enabled: bool = Field(True, env="OCR_ENABLED")
    ocr_language: str = Field("eng+hin", env="OCR_LANGUAGE")
    
    # RAG Settings
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    top_k_retrieval: int = Field(5, env="TOP_K_RETRIEVAL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        # Load environment variables
        load_dotenv()
        super().__init__(**kwargs)
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self, filename: str, format: str = None) -> Path:
        """Get output path for a specific format"""
        format = format or self.default_export_format
        format_dir = self.output_dir / format
        format_dir.mkdir(parents=True, exist_ok=True)
        return format_dir / filename
    
    @property
    def max_pdf_size_bytes(self) -> int:
        """Get max PDF size in bytes"""
        return self.max_pdf_size_mb * 1024 * 1024

# Singleton instance
_config_instance: Optional[Config] = None

def get_config() -> Config:
    """Get or create config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance