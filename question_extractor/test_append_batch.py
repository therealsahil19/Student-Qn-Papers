import sys
import json
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from question_extractor.append_batch import append_batch
except ImportError:
    # If running from within question_extractor/
    sys.path.append(str(Path(__file__).parent))
    try:
        from append_batch import append_batch
    except ImportError:
        raise

class TestAppendBatch(unittest.TestCase):
    def setUp(self):
        self.json_file = "test_input_correctness.json"
        self.target_file = "test_target_correctness.txt"

    def tearDown(self):
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        if os.path.exists(self.target_file):
            os.remove(self.target_file)

    def test_append_questions(self):
        questions = [
            {
                "category": "Loci",
                "marks": 3,
                "paper": "Paper 2024",
                "question": "Q1 Text"
            },
            {
                "category": "Loci",
                "marks": 4,
                "paper": "Paper 2024",
                "question": "Q2 Text"
            }
        ]

        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(questions, f)

        initial_content = """
Topic: Loci
Number of Questions: 0
"""
        with open(self.target_file, "w", encoding="utf-8") as f:
            f.write(initial_content)

        append_batch(self.json_file, self.target_file)

        with open(self.target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if Q1 and Q2 are present in correct format
        # The format is:
        # Q{i} (Marks {marks}) ({paper})
        # {question}

        expected_q1 = "\nQ1 (Marks 3) (Paper 2024)\nQ1 Text\n"
        expected_q2 = "\nQ2 (Marks 4) (Paper 2024)\nQ2 Text\n"

        self.assertIn(expected_q1, content)
        self.assertIn(expected_q2, content)

if __name__ == '__main__':
    unittest.main()
