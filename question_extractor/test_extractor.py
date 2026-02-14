import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from question_extractor.extractor import QuestionExtractor, ExtractedQuestion

class TestQuestionExtractor(unittest.TestCase):
    def setUp(self):
        self.tm_patcher = patch("question_extractor.extractor.TopicManager")
        self.MockTopicManager = self.tm_patcher.start()
        
        # Configure mock to avoid FileNotFoundError during init
        self.MockTopicManager.return_value.config_path.exists.return_value = True
        
        # Create a dummy config for testing if needed, or mock TopicManager
        self.extractor = QuestionExtractor(profile="test_profile")
        # Mock dependencies to avoid actual file I/O or external calls
        self.extractor.pdf_processor = MagicMock()
        # self.extractor.topic_manager is already mocked by the patcher, but we can refine it
        self.extractor.topic_manager = self.MockTopicManager.return_value

    def tearDown(self):
        self.tm_patcher.stop()

    def test_check_dependencies(self):
        """Test dependency checking."""
        self.extractor.pdf_processor.get_backend_info.return_value = {
            "backend": "mock",
            "available": True
        }
        
        status = self.extractor.check_dependencies()
        self.assertTrue(status["pdf_processor"])
        self.assertTrue(status["topics_config"])
        self.assertEqual(status["pdf_backend"], "mock")
        self.assertTrue(status["pdf_backend_available"])

    def test_get_extraction_progress(self):
        """Test extraction progress calculation."""
        # Add some dummy questions
        q1 = ExtractedQuestion("1", "Q1", "TopicA", "Unit1", source_paper="Paper1", page_number=1)
        q2 = ExtractedQuestion("2", "Q2", "TopicA", "Unit1", source_paper="Paper1", page_number=2)
        q3 = ExtractedQuestion("3", "Q3", "TopicB", "Unit2", source_paper="Paper2", page_number=1)

        self.extractor.add_question(q1)
        self.extractor.add_question(q2)
        self.extractor.add_question(q3)
        
        # Manually set processed pages for testing logic
        self.extractor.processed_pages = {
            "Paper1": [1, 2],
            "Paper2": [1]
        }

        # Test Paper1 progress
        progress1 = self.extractor.get_extraction_progress("Paper1", 10)
        self.assertEqual(progress1["source_paper"], "Paper1")
        self.assertEqual(progress1["total_pages"], 10)
        self.assertEqual(progress1["pages_processed"], 2)
        self.assertEqual(progress1["pages_remaining"], 8)
        self.assertEqual(progress1["questions_extracted"], 2)
        self.assertEqual(progress1["completion_percentage"], 20.0)

        # Test Paper2 progress
        progress2 = self.extractor.get_extraction_progress("Paper2", 5)
        self.assertEqual(progress2["questions_extracted"], 1)
        self.assertEqual(progress2["pages_processed"], 1)

if __name__ == '__main__':
    unittest.main()
