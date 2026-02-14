import unittest
import json
import os
import shutil
from pathlib import Path
from question_extractor.topic_manager import TopicManager

class TestTopicManager(unittest.TestCase):
    def setUp(self):
        self.test_config_dir = Path("./test_configs")
        self.test_config_dir.mkdir(exist_ok=True)
        self.config_path = self.test_config_dir / "test_profile.json"
        
        self.sample_config = {
            "syllabus_info": {"board": "TEST"},
            "units": {
                "Unit1": {
                    "enabled": True,
                    "topics": {
                        "Topic1": {"enabled": True, "full_name": "Test Topic 1"},
                        "Topic2": {"enabled": False, "full_name": "Test Topic 2"}
                    }
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.sample_config, f)

    def tearDown(self):
        if self.test_config_dir.exists():
            shutil.rmtree(self.test_config_dir)

    def test_init_load(self):
        """Test initializing and loading config."""
        manager = TopicManager(config_path=str(self.config_path))
        self.assertEqual(manager.get_syllabus_info()["board"], "TEST")

    def test_get_topics(self):
        """Test retrieving topics."""
        manager = TopicManager(config_path=str(self.config_path))
        
        # Test enabled topics
        enabled = manager.get_enabled_topics()
        self.assertIn("Topic1", enabled)
        self.assertNotIn("Topic2", enabled)
        
        # Test all topics
        all_topics = manager.get_all_topics()
        self.assertIn("Topic1", all_topics)
        self.assertIn("Topic2", all_topics)

    def test_enable_disable(self):
        """Test enabling and disabling topics."""
        manager = TopicManager(config_path=str(self.config_path))
        
        # Enable Topic2
        manager.enable_topic("Topic2")
        self.assertIn("Topic2", manager.get_enabled_topics())
        
        # Disable Topic1
        manager.disable_topic("Topic1")
        self.assertNotIn("Topic1", manager.get_enabled_topics())

if __name__ == '__main__':
    unittest.main()
