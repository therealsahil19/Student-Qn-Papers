"""
PDF Processor Module
Handles PDF to image conversion for visual analysis.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Any
import base64
from dataclasses import dataclass
import concurrent.futures

# Global variable to hold the open document in worker processes
_worker_doc = None
_worker_pdf_path = None

@dataclass
class PDFPage:
    """Represents a single page from a PDF."""
    page_number: int
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    width: int = 0
    height: int = 0


def _init_worker(pdf_path: str):
    """
    Initializer for worker processes.
    Opens the PDF file once per worker to avoid repeated open/close overhead.
    """
    global _worker_doc, _worker_pdf_path
    import fitz
    try:
        _worker_doc = fitz.open(str(pdf_path))
        _worker_pdf_path = str(pdf_path)
    except Exception as e:
        print(f"Failed to initialize worker with PDF {pdf_path}: {e}")
        _worker_doc = None
        _worker_pdf_path = None


def _process_page_task(args: Tuple[str, int, int, str, Optional[Path]]) -> Optional[PDFPage]:
    """
    Helper function to process a single page in a separate process.
    Must be at module level to be pickleable.
    """
    global _worker_doc, _worker_pdf_path
    pdf_path, page_num, dpi, output_format, output_dir = args
    import fitz

    # Use the pre-opened document from initializer if available
    doc = _worker_doc
    should_close = False

    # Check if we have a valid cached document for this PDF
    # If the document is not initialized, or if it belongs to a different PDF, open it
    if doc is None or _worker_pdf_path != str(pdf_path):
        # Close existing if it's a different PDF and open
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass

        # Fallback: Open document and cache it for future calls in this process
        doc = fitz.open(str(pdf_path))
        _worker_doc = doc
        _worker_pdf_path = str(pdf_path)
        should_close = False  # Keep it open for reuse

    if page_num < 1 or page_num > len(doc):
        if should_close:
            doc.close()
        return None

    page = doc[page_num - 1]  # 0-indexed

    # Calculate zoom for desired DPI (default PDF is 72 DPI)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=matrix)

    pdf_page = PDFPage(
        page_number=page_num,
        width=pix.width,
        height=pix.height
    )

    if output_dir:
        image_path = output_dir / f"page_{page_num:03d}.{output_format}"
        pix.save(str(image_path))
        pdf_page.image_path = str(image_path)
    else:
        # Return as base64
        img_bytes = pix.tobytes(output_format)
        pdf_page.image_base64 = base64.b64encode(img_bytes).decode('utf-8')

    if should_close:
        doc.close()

    return pdf_page


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
        
        # Get page count first to determine range
        # Optimization: Only open if we need to know the total pages (i.e. pages is None)
        if pages:
            page_numbers = list(pages)
            # Filter out non-positive page numbers
            # We rely on the worker to handle the upper bound check since we don't have total_pages
            valid_page_numbers = [p for p in page_numbers if p >= 1]
        else:
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            doc.close()

            page_numbers = range(1, total_pages + 1)
            valid_page_numbers = list(page_numbers)
        
        # Prepare arguments for each task
        tasks = []
        for page_num in valid_page_numbers:
            tasks.append((
                str(pdf_path),
                page_num,
                self.dpi,
                self.output_format,
                output_dir
            ))
            
        result = []
        # Use ProcessPoolExecutor for parallel processing
        # Initialize each worker with the PDF file to avoid repeated opens
        with concurrent.futures.ProcessPoolExecutor(
            initializer=_init_worker,
            initargs=(str(pdf_path),)
        ) as executor:
            # Map returns results in order
            results = executor.map(_process_page_task, tasks)
            
            for res in results:
                if res:
                    result.append(res)

        return result
    
    def _convert_with_pdf2image(
        self, 
        pdf_path: Path, 
        output_dir: Optional[Path],
        pages: Optional[List[int]]
    ) -> List[PDFPage]:
        """Convert using pdf2image with memory optimization."""
        from pdf2image import convert_from_path, pdfinfo_from_path
        import io
        
        chunk_size = 50  # Process pages in chunks to reduce memory usage
        result = []
        
        # Determine the full range of pages to process
        if pages:
            start_page = min(pages)
            end_page = max(pages)
            pages_set = set(pages)
        else:
            # Get total page count using pdfinfo
            try:
                info = pdfinfo_from_path(str(pdf_path))
                total_pages = int(info["Pages"])
                start_page = 1
                end_page = total_pages
                pages_set = None
            except Exception:
                # Fallback: if we can't get page count, try to read reasonable amount or just fallback to load all
                # Ideally pdfinfo works if convert_from_path works.
                # If it fails, we fall back to loading everything (legacy behavior)
                # but we need to know the range.
                # Without page count, we can't loop effectively without risk.
                # So we just do what we did before: load all.
                kwargs = {"dpi": self.dpi}
                images = convert_from_path(str(pdf_path), **kwargs)
                for i, img in enumerate(images):
                    page_num = i + 1
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
                        buffer = io.BytesIO()
                        img.save(buffer, format=self.output_format.upper())
                        pdf_page.image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    result.append(pdf_page)
                return result

        # Process in chunks
        for chunk_start in range(start_page, end_page + 1, chunk_size):
            chunk_end = min(chunk_start + chunk_size - 1, end_page)
            
            # Optimize: Check if any pages in this chunk are actually needed
            if pages_set:
                chunk_pages = set(range(chunk_start, chunk_end + 1))
                if not chunk_pages.intersection(pages_set):
                    continue
            
            try:
                images = convert_from_path(
                    str(pdf_path),
                    dpi=self.dpi,
                    first_page=chunk_start,
                    last_page=chunk_end
                )
            except Exception:
                # Stop if we hit an error
                break
            
            for i, img in enumerate(images):
                page_num = chunk_start + i

                # Filter if specific pages requested
                if pages_set and page_num not in pages_set:
                    continue

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

            # Free memory
            del images
        
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
