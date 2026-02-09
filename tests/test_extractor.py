
import unittest
import json
from question_extractor.extractor import QuestionExtractor, ExtractedQuestion

class TestQuestionExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = QuestionExtractor()
        
    def test_add_questions_from_json_valid(self):
        json_data = json.dumps({
            "questions": [
                {
                    "question_number": "1",
                    "question_text": "What is 2+2?",
                    "topic": "Algebra",
                    "marks": 1
                }
            ]
        })
        count = self.extractor.add_questions_from_json(json_data, source_paper="Test Paper")
        self.assertEqual(count, 1)
        self.assertEqual(len(self.extractor.extracted_questions), 1)
        self.assertEqual(self.extractor.extracted_questions[0].question_text, "What is 2+2?")

    def test_add_questions_from_json_markdown_block(self):
        json_content = json.dumps({
            "questions": [
                {
                    "question_number": "2",
                    "question_text": "Resolve into factors",
                    "topic": "Algebra"
                }
            ]
        })
        markdown_data = f"Here is the output:\n```json\n{json_content}\n```"
        count = self.extractor.add_questions_from_json(markdown_data, source_paper="Test Paper")
        self.assertEqual(count, 1)
        self.assertEqual(self.extractor.extracted_questions[0].question_number, "2")

    def test_add_questions_from_json_invalid(self):
        invalid_json = "{invalid_json}"
        with self.assertRaises(ValueError):
            self.extractor.add_questions_from_json(invalid_json)

    def test_add_questions_with_duplicate_check(self):
        q1 = {
            "question_number": "1",
            "question_text": "Q1",
            "topic": "T1"
        }
        json_data = json.dumps({"questions": [q1]})
        
        # Add first time
        self.extractor.add_questions_from_json(json_data, source_paper="Paper1")
        self.assertEqual(len(self.extractor.extracted_questions), 1)
        
        # Add duplicate (same number and source)
        self.extractor.add_questions_from_json(json_data, source_paper="Paper1")
        self.assertEqual(len(self.extractor.extracted_questions), 1)
        
        # Add same question number but different source
        self.extractor.add_questions_from_json(json_data, source_paper="Paper2")
        self.assertEqual(len(self.extractor.extracted_questions), 2)

if __name__ == '__main__':
    unittest.main()
