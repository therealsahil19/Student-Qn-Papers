
import unittest
import sys
import os
from typing import List

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_extractor.paper_generator import QuestionBankParser, PaperBuilder, Question, Section

class TestQuestionBankParser(unittest.TestCase):
    def setUp(self):
        self.parser = QuestionBankParser()

    def test_parse_content_simple(self):
        content = """
Topic: Algebra
--------------------------------------------------
Q1 [2 marks] (easy)
    Find x if 2x = 4.
    [Source: 2024]

Q2 [4 marks] (medium)
    Solve x^2 - 4 = 0.
"""
        questions = self.parser.parse_content(content)
        self.assertEqual(len(questions), 2)
        
        q1 = questions[0]
        self.assertEqual(q1.number, "Q1")
        self.assertEqual(q1.marks, 2)
        self.assertEqual(q1.difficulty, "easy")
        self.assertEqual(q1.topic, "Algebra")
        self.assertIn("Find x", q1.text)
        
        q2 = questions[1]
        self.assertEqual(q2.number, "Q2")
        self.assertEqual(q2.marks, 4)

    def test_parse_content_with_figure(self):
        content = """
Topic: Geometry
--------------------------------------------------
Q3 [3 marks] (hard)
    Find the area.
    [FIGURE]
    type: circle
    description: Unit circle
    [/FIGURE]
"""
        questions = self.parser.parse_content(content)
        self.assertEqual(len(questions), 1)
        self.assertIn("type: circle", questions[0].figure_block)

class TestPaperBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PaperBuilder()

    def test_auto_select_sections(self):
        # Create dummy questions
        questions = []
        # 15 MCQs (1 mark)
        for i in range(15):
            questions.append(Question(f"Q{i}", 1, "easy", "text", "topic", is_mcq=True))
        
        # 5 Short answer (4 marks)
        for i in range(5):
            questions.append(Question(f"Q{i+15}", 4, "medium", "text", "topic"))
            
        # 5 Long answer (8 marks)
        for i in range(5):
            questions.append(Question(f"Q{i+20}", 8, "hard", "text", "topic"))

        sections = self.builder._auto_select_sections(questions, 80)
        
        # Check Section A (MCQs)
        section_a = next(s for s in sections if s.name == "Section A")
        self.assertEqual(len(section_a.questions), 10)  # Should pick 10 MCQs
        
        # Check Section B
        section_b = next(s for s in sections if s.name == "Section B")
        self.assertTrue(len(section_b.questions) > 0)

if __name__ == '__main__':
    unittest.main()
