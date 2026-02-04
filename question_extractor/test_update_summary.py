import unittest
import os
import shutil
import re
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(os.getcwd())

try:
    from question_extractor.update_summary import update_file_summary
except ImportError:
    sys.path.append('question_extractor')
    from update_summary import update_file_summary

class TestUpdateSummary(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_summary_update.txt"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_update_summary_counts(self):
        # Create a file with incorrect counts
        content = """
Topic: Algebra
Number of Questions: 0
--------------------------------------------------
Q1
...
Q2
...
--------------------------------------------------

Topic: Geometry
Number of Questions: 999
--------------------------------------------------
Q1
...
Q2
...
Q3
...
--------------------------------------------------

SUMMARY
=======
  Algebra: 0 questions
  Geometry: 999 questions
=======
"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)

        update_file_summary(self.test_file)

        with open(self.test_file, 'r', encoding='utf-8') as f:
            new_content = f.read()

        # Verify counts in headers
        self.assertRegex(new_content, r'Topic: Algebra\nNumber of Questions: 2')
        self.assertRegex(new_content, r'Topic: Geometry\nNumber of Questions: 3')

        # Verify summary
        self.assertIn("Algebra: 2 questions", new_content)
        self.assertIn("Geometry: 3 questions", new_content)
        self.assertIn("Total questions: 5", new_content)

if __name__ == '__main__':
    unittest.main()
