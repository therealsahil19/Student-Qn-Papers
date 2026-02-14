import unittest
from question_extractor.figure_renderer import PointLayoutEngine, RenderConfig
from question_extractor.geometry_schema import GeometryFigure, Point, FigureType

class TestFigureRendererSolver(unittest.TestCase):
    def setUp(self):
        self.config = RenderConfig()
        self.engine = PointLayoutEngine(self.config)

    def test_recursive_solver(self):
        # Create a figure with a chain of dependencies
        # A (0,0) -> B (Description: "on segment AC") -> Wait, need C.
        # Let's do:
        # A: (0,0)
        # B: (10,0)
        # C: midpoint of AB -> (5,0)
        # D: midpoint of AC -> (2.5, 0)
        
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Test recursive solver"
        )
        
        figure.points.append(Point(label="A", x=0, y=0))
        figure.points.append(Point(label="B", x=10, y=0))
        figure.points.append(Point(label="C", description="midpoint of AB"))
        figure.points.append(Point(label="D", description="midpoint of AC"))
        
        positions = self.engine.calculate_positions(figure)
        
        self.assertIn("A", positions)
        self.assertIn("B", positions)
        self.assertIn("C", positions)
        self.assertIn("D", positions)
        
        self.assertEqual(positions["C"], (5.0, 0.0))
        self.assertEqual(positions["D"], (2.5, 0.0))

if __name__ == '__main__':
    unittest.main()
