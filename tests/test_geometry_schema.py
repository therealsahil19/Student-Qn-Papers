
import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_extractor.geometry_schema import FigureParser, FigureValidator, GeometryFigure, FigureType

class TestFigureParser(unittest.TestCase):
    def setUp(self):
        self.parser = FigureParser()
    
    def test_parse_yaml_valid(self):
        yaml_block = """
type: circle_tangent
description: Test Description
elements:
  - circle: {center: O, radius: 3}
"""
        figure = self.parser.parse(yaml_block)
        self.assertEqual(figure.figure_type, FigureType.CIRCLE_TANGENT)
        self.assertEqual(figure.description, "Test Description")
        self.assertEqual(len(figure.circles), 1)

    def test_normalize_yaml_block_standard(self):
        block = """
type: test
description: desc
"""
        # Leading newline is common
        normalized = self.parser._normalize_yaml_block(block)
        self.assertIn("type: test", normalized)

    def test_normalize_yaml_block_indented(self):
        # Simulate extraction where first line is stripped but others are indented
        block = """type: test
    description: desc
    elements: []"""
        
        normalized = self.parser._normalize_yaml_block(block)
        # Should dedent subsequent lines
        expected = "type: test\ndescription: desc\nelements: []"
        self.assertEqual(normalized, expected)

    def test_normalize_yaml_block_mixed(self):
        # Indented first line
        block = """
    type: test
    description: desc
        """
        normalized = self.parser._normalize_yaml_block(block)
        self.assertIn("type: test", normalized)
        self.assertIn("description: desc", normalized)

    def test_parse_simple_format(self):
        block = """
type: generic
description: simple description
image_ref: path/to/image.png
"""
        figure = self.parser.parse(block)
        self.assertEqual(figure.figure_type, FigureType.GENERIC)
        self.assertEqual(figure.description, "simple description")
        self.assertEqual(figure.image_ref, "path/to/image.png")

    def test_parse_from_question(self):
        text = """
Q1. [FIGURE]
type: generic
description: inside
[/FIGURE]
        """
        figure = self.parser.parse_from_question(text)
        self.assertIsNotNone(figure)
        self.assertEqual(figure.description, "inside")

class TestFigureValidator(unittest.TestCase):
    def setUp(self):
        self.validator = FigureValidator()
    
    def test_validate_valid_figure(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Valid figure"
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)

    def test_validate_missing_description(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description=""
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Missing figure description", issues)

if __name__ == '__main__':
    unittest.main()
