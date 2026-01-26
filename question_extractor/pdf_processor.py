"""
PDF Processor Module
Handles PDF to image conversion for visual analysis.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
import base64
from dataclasses import dataclass


@dataclass
class PDFPage:
    """Represents a single page from a PDF."""
    page_number: int
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    width: int = 0
    height: int = 0


class PDFProcessor:
    """
    Converts PDF files to images for visual analysis.
    
    Supports multiple backends:
    - pdf2image (requires poppler)
    - PyMuPDF (fitz)
    """
    
    def __init__(self, dpi: int = 200, output_format: str = "png"):
        """
        Initialize the PDF processor.
        
        Args:
            dpi: Resolution for image conversion (default 200)
            output_format: Output image format (png, jpg)
        """
        self.dpi = dpi
        self.output_format = output_format
        self._backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        """Detect available PDF processing backend."""
        try:
            import fitz  # PyMuPDF
            return "pymupdf"
        except ImportError:
            pass
        
        try:
            from pdf2image import convert_from_path
            return "pdf2image"
        except ImportError:
            pass
        
        return "none"
    
    def get_backend_info(self) -> dict:
        """Get information about the current backend."""
        return {
            "backend": self._backend,
            "available": self._backend != "none",
            "install_instructions": self._get_install_instructions()
        }
    
    def _get_install_instructions(self) -> str:
        """Get installation instructions for PDF processing libraries."""
        return """
To enable PDF processing, install one of the following:

Option 1: PyMuPDF (Recommended - pure Python, no external dependencies)
    pip install PyMuPDF

Option 2: pdf2image (Requires Poppler)
    pip install pdf2image
    # Also install Poppler:
    # Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
    # macOS: brew install poppler
    # Linux: sudo apt-get install poppler-utils
"""
    
    def convert_pdf_to_images(
        self, 
        pdf_path: str, 
        output_dir: Optional[str] = None,
        pages: Optional[List[int]] = None
    ) -> List[PDFPage]:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save images (optional, if None returns base64)
            pages: Specific page numbers to convert (1-indexed), None for all
            
        Returns:
            List of PDFPage objects with image data
        """
        if self._backend == "none":
            raise RuntimeError(
                "No PDF processing backend available. " + 
                self._get_install_instructions()
            )
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        if self._backend == "pymupdf":
            return self._convert_with_pymupdf(pdf_path, output_dir, pages)
        else:
            return self._convert_with_pdf2image(pdf_path, output_dir, pages)
    
    def _convert_with_pymupdf(
        self, 
        pdf_path: Path, 
        output_dir: Optional[Path],
        pages: Optional[List[int]]
    ) -> List[PDFPage]:
        """Convert using PyMuPDF."""
        import fitz
        
        result = []
        doc = fitz.open(str(pdf_path))
        
        page_numbers = pages if pages else range(1, len(doc) + 1)
        
        for page_num in page_numbers:
            if page_num < 1 or page_num > len(doc):
                continue
                
            page = doc[page_num - 1]  # 0-indexed
            
            # Calculate zoom for desired DPI (default PDF is 72 DPI)
            zoom = self.dpi / 72
            matrix = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=matrix)
            
            pdf_page = PDFPage(
                page_number=page_num,
                width=pix.width,
                height=pix.height
            )
            
            if output_dir:
                image_path = output_dir / f"page_{page_num:03d}.{self.output_format}"
                pix.save(str(image_path))
                pdf_page.image_path = str(image_path)
            else:
                # Return as base64
                img_bytes = pix.tobytes(self.output_format)
                pdf_page.image_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            result.append(pdf_page)
        
        doc.close()
        return result
    
    def _convert_with_pdf2image(
        self, 
        pdf_path: Path, 
        output_dir: Optional[Path],
        pages: Optional[List[int]]
    ) -> List[PDFPage]:
        """Convert using pdf2image."""
        from pdf2image import convert_from_path
        import io
        
        # Convert pages to pdf2image format (first_page, last_page)
        kwargs = {"dpi": self.dpi}
        if pages:
            kwargs["first_page"] = min(pages)
            kwargs["last_page"] = max(pages)
        
        images = convert_from_path(str(pdf_path), **kwargs)
        result = []
        
        for i, img in enumerate(images):
            page_num = (pages[i] if pages else i + 1)
            
            pdf_page = PDFPage(
                page_number=page_num,
                width=img.width,
                height=img.height
            )
            
            if output_dir:
                image_path = output_dir / f"page_{page_num:03d}.{self.output_format}"
                img.save(str(image_path), self.output_format.upper())
                pdf_page.image_path = str(image_path)
            else:
                # Return as base64
                buffer = io.BytesIO()
                img.save(buffer, format=self.output_format.upper())
                pdf_page.image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            result.append(pdf_page)
        
        return result
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic information about a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        if self._backend == "pymupdf":
            import fitz
            doc = fitz.open(pdf_path)
            info = {
                "page_count": len(doc),
                "metadata": doc.metadata,
                "filename": Path(pdf_path).name
            }
            doc.close()
            return info
        elif self._backend == "pdf2image":
            from pdf2image import pdfinfo_from_path
            info = pdfinfo_from_path(pdf_path)
            return {
                "page_count": info.get("Pages", 0),
                "filename": Path(pdf_path).name
            }
        else:
            return {"error": "No backend available", "filename": Path(pdf_path).name}


# Convenience function
def pdf_to_images(pdf_path: str, output_dir: str = None, dpi: int = 200) -> List[PDFPage]:
    """
    Convenience function to convert a PDF to images.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save images (optional)
        dpi: Image resolution
        
    Returns:
        List of PDFPage objects
    """
    processor = PDFProcessor(dpi=dpi)
    return processor.convert_pdf_to_images(pdf_path, output_dir)
