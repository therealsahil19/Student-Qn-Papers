import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from question_extractor.diagram_utils import ensure_output_directory, create_diagram

class TestDiagramUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("./test_output_utils")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_ensure_output_directory(self):
        """Test directory creation."""
        path = ensure_output_directory(str(self.test_dir))
        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())
        
        # Should not fail if exists
        path2 = ensure_output_directory(str(self.test_dir))
        self.assertEqual(path, path2)

    @patch("question_extractor.diagram_utils.FigureParser")
    @patch("question_extractor.diagram_utils.FigureRenderer")
    def test_create_diagram(self, MockRenderer, MockParser):
        """Test diagram creation orchestration."""
        # Setup mocks
        mock_renderer_instance = MockRenderer.return_value
        mock_parser_instance = MockParser.return_value
        
        # Create dir
        self.test_dir.mkdir()
        
        # Execute
        result = create_diagram("test_diag", "content", self.test_dir, "svg")
        
        # Verify
        mock_parser_instance.parse.assert_called_with("content")
        mock_renderer_instance.render.assert_called()
        mock_renderer_instance.save_svg.assert_called()
        self.assertTrue(result.endswith("test_diag.svg"))

if __name__ == '__main__':
    unittest.main()
