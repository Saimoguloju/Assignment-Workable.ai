"""Export functionality for different formats"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import tempfile

from .formatter import Formatter
from ..utils.file_handler import FileHandler
from ..core.config import get_config

class Exporter:
    """Export questions to various formats"""
    
    def __init__(self):
        """Initialize exporter"""
        self.formatter = Formatter()
        self.file_handler = FileHandler()
        self.config = get_config()
    
    def export_latex(self, questions: List[Dict], filepath: Optional[Path] = None) -> str:
        """Export questions as LaTeX
        
        Args:
            questions: List of questions
            filepath: Optional output filepath
            
        Returns:
            LaTeX content
        """
        latex_content = self.formatter.format_latex(questions)
        
        if filepath:
            self.file_handler.save_latex(latex_content, filepath)
        
        return latex_content
    
    def export_markdown(self, questions: List[Dict], filepath: Optional[Path] = None) -> str:
        """Export questions as Markdown
        
        Args:
            questions: List of questions
            filepath: Optional output filepath
            
        Returns:
            Markdown content
        """
        md_content = self.formatter.format_markdown(questions)
        
        if filepath:
            self.file_handler.save_markdown(md_content, filepath)
        
        return md_content
    
    def export_json(self, questions: List[Dict], filepath: Optional[Path] = None) -> str:
        """Export questions as JSON
        
        Args:
            questions: List of questions
            filepath: Optional output filepath
            
        Returns:
            JSON string
        """
        json_data = self.formatter.format_json(questions)
        json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        if filepath:
            self.file_handler.save_json(json_data, filepath)
        
        return json_content
    
    def export_pdf(self, questions: List[Dict], filepath: Optional[Path] = None) -> Optional[bytes]:
        """Export questions as PDF (requires LaTeX installation)
        
        Args:
            questions: List of questions
            filepath: Optional output filepath
            
        Returns:
            PDF bytes or None if failed
        """
        try:
            # Create LaTeX content
            latex_content = self.formatter.format_latex(questions)
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save LaTeX file
                tex_file = Path(tmpdir) / "questions.tex"
                tex_file.write_text(latex_content)
                
                # Compile LaTeX to PDF
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", str(tex_file)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Read PDF
                    pdf_file = Path(tmpdir) / "questions.pdf"
                    if pdf_file.exists():
                        pdf_bytes = pdf_file.read_bytes()
                        
                        if filepath:
                            filepath.write_bytes(pdf_bytes)
                        
                        return pdf_bytes
                else:
                    print(f"LaTeX compilation failed: {result.stderr}")
                    return None
        except FileNotFoundError:
            print("pdflatex not found. Please install LaTeX.")
            return None
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def export_all_formats(self, questions: List[Dict], base_filename: str) -> Dict[str, Path]:
        """Export questions in all formats
        
        Args:
            questions: List of questions
            base_filename: Base filename without extension
            
        Returns:
            Dictionary of format to filepath
        """
        output_files = {}
        
        # LaTeX
        latex_file = self.config.get_output_path(f"{base_filename}.tex", "latex")
        self.export_latex(questions, latex_file)
        output_files['latex'] = latex_file
        
        # Markdown
        md_file = self.config.get_output_path(f"{base_filename}.md", "markdown")
        self.export_markdown(questions, md_file)
        output_files['markdown'] = md_file
        
        # JSON
        json_file = self.config.get_output_path(f"{base_filename}.json", "json")
        self.export_json(questions, json_file)
        output_files['json'] = json_file
        
        # PDF (if LaTeX is available)
        pdf_file = self.config.get_output_path(f"{base_filename}.pdf", "pdf")
        if self.export_pdf(questions, pdf_file):
            output_files['pdf'] = pdf_file
        
        return output_files