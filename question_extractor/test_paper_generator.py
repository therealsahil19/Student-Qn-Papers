import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock dependencies before importing paper_generator
# We need to ensure we can import even if dependencies are missing, 
# although paper_generator handles imports gracefully.
from question_extractor.paper_generator import (
    BasePaperGenerator, 
    QuestionBankParser,
    Question,
    Section
)

class TestQuestionBankParser(unittest.TestCase):
    def setUp(self):
        self.parser = QuestionBankParser()

    def test_split_sections(self):
        content = "Header\nTopic: Algebra\nQ1\nTopic: Geometry\nQ2"
        parts = self.parser._split_sections(content)
        # Splits: ['Header\n', 'Algebra', '\nQ1\n', 'Geometry', '\nQ2']
        # The regex keeps the capturing group (Topic name).
        # re.split(pattern, string) with capturing group returns [pre, cap1, post, cap2, post...]
        # Verify length and content
        self.assertTrue(len(parts) >= 3)
        self.assertEqual(parts[1], "Algebra")
        self.assertEqual(parts[3], "Geometry")

class TestBasePaperGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = BasePaperGenerator(render_figures=False)

    def test_cleanup_temp_images(self):
        # Patch os.unlink where it is used in paper_generator module
        with patch('question_extractor.paper_generator.os.unlink') as mock_unlink:
            self.generator.temp_images = ['tmp1.png', 'tmp2.png']
            self.generator._cleanup_temp_images()
            self.assertEqual(mock_unlink.call_count, 2)
            self.assertEqual(self.generator.temp_images, [])

if __name__ == '__main__':
    unittest.main()
