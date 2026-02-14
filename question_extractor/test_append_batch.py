import sys
import json
import os
import unittest
import shutil
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

class TestAppendBatchRefactor(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_batch"
        os.makedirs(self.test_dir, exist_ok=True)
        self.json_file = os.path.join(self.test_dir, "questions.json")
        self.target_file = os.path.join(self.test_dir, "question_bank.txt")

        # Create dummy json
        questions = [
            {"category": "Similarity", "marks": 3, "paper": "2024", "question": "Prove triangles similar."},
            {"category": "Loci", "marks": 2, "paper": "2023", "question": "Find locus."}
        ]
        with open(self.json_file, 'w') as f:
            json.dump(questions, f)

        # Create dummy target file
        content = """
Topic: Similarity
Q1. Old question.

Topic: Circles
Q2. Circle question.

CUMULATIVE SUMMARY
"""
        with open(self.target_file, 'w') as f:
            f.write(content)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_append_batch(self):
        # Run append_batch
        append_batch(self.json_file, self.target_file)

        # Verify content
        with open(self.target_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Prove triangles similar", content)
        
        sim_idx = content.find("Topic: Similarity")
        old_q_idx = content.find("Old question", sim_idx)
        new_q_idx = content.find("Prove triangles similar", sim_idx)
        
        self.assertTrue(old_q_idx < new_q_idx, "New question should be after old question in section")
        
        self.assertNotIn("Find locus", content)

if __name__ == '__main__':
    unittest.main()