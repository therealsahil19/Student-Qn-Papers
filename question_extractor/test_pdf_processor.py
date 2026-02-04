
import unittest
import os
import shutil
from pathlib import Path
from question_extractor.pdf_processor import PDFProcessor
import sys

# Ensure reportlab is available for test generation
try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

class TestPDFProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not canvas:
            raise unittest.SkipTest("Reportlab not installed")

        cls.pdf_path = "test_processor_fixture.pdf"
        cls.generate_pdf(cls.pdf_path, 10)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.pdf_path):
            os.remove(cls.pdf_path)

    @classmethod
    def generate_pdf(cls, filename, pages=10):
        c = canvas.Canvas(filename)
        for i in range(pages):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        c.save()

    def test_pages_provided(self):
        """Test processing specific pages (Optimization path)"""
        processor = PDFProcessor()
        # Test getting specific page
        pages = processor.convert_pdf_to_images(self.pdf_path, pages=[1])
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].page_number, 1)
        self.assertIsNotNone(pages[0].image_base64)

        # Test out of bounds (should be handled gracefully)
        # Note: Worker returns None, processor filters None.
        pages = processor.convert_pdf_to_images(self.pdf_path, pages=[999])
        self.assertEqual(len(pages), 0)

    def test_pages_none(self):
        """Test processing all pages (Standard path)"""
        processor = PDFProcessor()
        pages = processor.convert_pdf_to_images(self.pdf_path)
        self.assertEqual(len(pages), 10)
        self.assertEqual(pages[0].page_number, 1)
        self.assertEqual(pages[9].page_number, 10)

if __name__ == '__main__':
    unittest.main()
