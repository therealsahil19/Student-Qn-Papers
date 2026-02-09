import unittest
from question_extractor.geometry_schema import (
    GeometryFigure, FigureType, Point, Line, Circle,
    Angle, Triangle, Quadrilateral, FigureValidator
)

class TestGeometrySchema(unittest.TestCase):
    def setUp(self):
        self.validator = FigureValidator()

    def test_get_all_point_labels(self):
        figure = GeometryFigure(
            figure_type=FigureType.CIRCLE_INSCRIBED_ANGLE,
            description="Test figure"
        )
        figure.points = [Point(label="A"), Point(label="B")]
        figure.lines = [Line(start="B", end="C")]
        figure.circles = [Circle(center="O", points_on_circle=["A", "D"])]

        labels = figure.get_all_point_labels()
        self.assertEqual(labels, ["A", "B", "C", "D", "O"])

    def test_validate_success(self):
        figure = GeometryFigure(
            figure_type=FigureType.CIRCLE_INSCRIBED_ANGLE,
            description="Circle with triangle ABC",
            points=[Point(label="A"), Point(label="B"), Point(label="C"), Point(label="O")],
            circles=[Circle(center="O", points_on_circle=["A", "B", "C"])],
            triangles=[Triangle(vertices=("A", "B", "C"))]
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

    def test_validate_generic_with_elements(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Generic but has elements",
            circles=[Circle(center="O")]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Figure has elements but type is 'generic' - consider specifying type", issues)

    def test_validate_invalid_angle_vertex(self):
        figure = GeometryFigure(
            figure_type=FigureType.TRIANGLE_PROPERTIES,
            description="Triangle ABC",
            points=[Point(label="A"), Point(label="B"), Point(label="C")],
            angles=[Angle(vertex="X", ray1_end="A", ray2_end="B")]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Angle vertex 'X' not found in structural elements", issues)

    def test_validate_duplicate_points(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Duplicate points",
            points=[Point(label="A"), Point(label="A")]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Duplicate definition for point 'A'", issues)

    def test_validate_invalid_line(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Invalid line",
            lines=[Line(start="A", end="A")]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Line has same start and end point 'A'", issues)

    def test_validate_invalid_triangle(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Invalid triangle",
            triangles=[Triangle(vertices=("A", "A", "B"))]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Triangle ('A', 'A', 'B') must have 3 distinct vertices", issues)

    def test_validate_invalid_quadrilateral(self):
        figure = GeometryFigure(
            figure_type=FigureType.GENERIC,
            description="Invalid quad",
            quadrilaterals=[Quadrilateral(vertices=("A", "B", "C", "A"))]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Quadrilateral ('A', 'B', 'C', 'A') must have 4 distinct vertices", issues)

    def test_validate_angle_rays(self):
        figure = GeometryFigure(
            figure_type=FigureType.TRIANGLE_PROPERTIES,
            description="Invalid angle rays",
            points=[Point(label="A"), Point(label="B")],
            angles=[Angle(vertex="A", ray1_end="B", ray2_end="C")]
        )
        is_valid, issues = self.validator.validate(figure)
        self.assertFalse(is_valid)
        self.assertIn("Angle ray end 'C' not found in structural elements", issues)

if __name__ == "__main__":
    unittest.main()
