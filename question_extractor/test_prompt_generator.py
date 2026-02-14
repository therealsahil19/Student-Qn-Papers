import unittest
from unittest.mock import MagicMock
from question_extractor.prompt_generator import PromptGenerator

class TestPromptGenerator(unittest.TestCase):
    def setUp(self):
        self.topic_manager = MagicMock()
        self.generator = PromptGenerator(self.topic_manager)
        
        # Setup mock topic data
        self.topic_manager.get_all_topics.return_value = {
            "Topic1": {
                "full_name": "Full Topic 1",
                "unit": "Unit 1",
                "keywords": ["kw1", "kw2"],
                "subtopics": ["sub1"],
                "formulas": ["f1"]
            },
            "Topic2": {
                "full_name": "Full Topic 2",
                "unit": "Unit 2",
                "keywords": ["kw3"]
            }
        }
        self.topic_manager.get_enabled_topics.return_value = {
            "Topic1": {}
        }
        self.topic_manager.get_extraction_settings.return_value = {}
        self.topic_manager.get_syllabus_info.return_value = {"board": "TEST", "class": "99"}

    def test_generate_extraction_prompt_specific_topics(self):
        """Test prompt generation with specific topics."""
        prompt = self.generator.generate_extraction_prompt(topics=["Topic1"])
        
        self.assertIn("Full Topic 1", prompt)
        self.assertIn("kw1, kw2", prompt)
        self.assertIn("Unit 1", prompt)
        self.assertIn("TEST Class 99", prompt)
        # Should not include Topic2
        self.assertNotIn("Full Topic 2", prompt)

    def test_generate_extraction_prompt_default_topics(self):
        """Test prompt generation with default enabled topics."""
        prompt = self.generator.generate_extraction_prompt()
        
        self.assertIn("Full Topic 1", prompt)
        # Mock says only Topic1 is enabled
        self.assertNotIn("Full Topic 2", prompt)

if __name__ == '__main__':
    unittest.main()
