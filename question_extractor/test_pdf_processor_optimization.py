
import unittest
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add parent directory to path to import pdf_processor
sys.path.append(str(Path(__file__).parent.parent))

from question_extractor.pdf_processor import PDFProcessor

class TestPDFProcessorOptimization(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()
        # Force backend to pymupdf for these tests
        self.processor._backend = "pymupdf"

    @patch('pathlib.Path.exists')
    @patch('fitz.open')
    def test_page_count_optimization(self, mock_fitz_open, mock_exists):
        """Test that fitz.open is NOT called when page_count is provided."""
        mock_exists.return_value = True
        pdf_path = "test.pdf"
        page_count = 10

        # Mock executor to avoid actually running tasks
        with patch('concurrent.futures.ProcessPoolExecutor') as mock_executor:
            # Setup mock future
            mock_executor_instance = mock_executor.return_value
            mock_executor_instance.__enter__.return_value = mock_executor_instance
            mock_executor_instance.map.return_value = [] # Return empty list

            # Call with page_count
            self.processor.convert_pdf_to_images(
                pdf_path,
                page_count=page_count
            )

            # Verification: fitz.open should NOT be called in the main thread
            # Note: It might be called inside workers, but we mocked ProcessPoolExecutor
            # and _init_worker is called inside workers.
            # However, _init_worker imports fitz and calls open. But we patched fitz.open in this process.
            # Wait, patch only patches in the current process. Workers are new processes.
            # But here we are verifying the MAIN process logic.

            mock_fitz_open.assert_not_called()

    @patch('pathlib.Path.exists')
    @patch('fitz.open')
    def test_no_page_count_context_manager(self, mock_fitz_open, mock_exists):
        """Test that fitz.open IS called when page_count is NOT provided, and used as context manager."""
        mock_exists.return_value = True
        pdf_path = "test.pdf"

        # Mock the document object returned by context manager
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        # Mock executor
        with patch('concurrent.futures.ProcessPoolExecutor') as mock_executor:
            mock_executor_instance = mock_executor.return_value
            mock_executor_instance.__enter__.return_value = mock_executor_instance
            mock_executor_instance.map.return_value = []

            # Call without page_count
            self.processor.convert_pdf_to_images(pdf_path)

            # Verification: fitz.open should be called
            mock_fitz_open.assert_called_once_with(str(Path(pdf_path)))

            # Verify context manager usage
            mock_fitz_open.return_value.__enter__.assert_called()
            mock_fitz_open.return_value.__exit__.assert_called()

if __name__ == '__main__':
    unittest.main()
