"""
Geometry Figure Schema Module

Defines structured schemas for representing geometric figures in ICSE Class 10 Math questions.
Supports parsing [FIGURE]...[/FIGURE] blocks from question text files.

Usage:
    from geometry_schema import FigureParser, GeometryFigure
    
    parser = FigureParser()
    figure = parser.parse(figure_block_text)
    print(figure.to_dict())
"""

import re
import yaml
import textwrap
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


class FigureType(Enum):
    """Supported geometry figure types for ICSE Class 10."""
    
    # Circle-related
    CIRCLE_INSCRIBED_ANGLE = "circle_inscribed_angle"
    CIRCLE_TANGENT = "circle_tangent"
    CIRCLE_CHORD = "circle_chord"
    CIRCLE_SECANT = "circle_secant"
    CYCLIC_QUADRILATERAL = "cyclic_quadrilateral"
    ALTERNATE_SEGMENT = "alternate_segment"
    
    # Triangle-related  
    SIMILAR_TRIANGLES = "similar_triangles"
    CONGRUENT_TRIANGLES = "congruent_triangles"
    TRIANGLE_PROPERTIES = "triangle_properties"
    BPT_TRIANGLE = "bpt_triangle"  # Basic Proportionality Theorem
    
    # Construction-related
    CONSTRUCTION_TANGENT = "construction_tangent"
    CONSTRUCTION_CIRCUMCIRCLE = "construction_circumcircle"
    CONSTRUCTION_INCIRCLE = "construction_incircle"
    CONSTRUCTION_LOCUS = "construction_locus"
    
    # Coordinate geometry
    COORDINATE_POINTS = "coordinate_points"
    COORDINATE_LINE = "coordinate_line"
    COORDINATE_REFLECTION = "coordinate_reflection"
    
    # 3D Mensuration
    MENSURATION_CYLINDER = "mensuration_cylinder"
    MENSURATION_CONE = "mensuration_cone"
    MENSURATION_SPHERE = "mensuration_sphere"
    MENSURATION_COMBINED = "mensuration_combined"
    
    # Generic
    GENERIC = "generic"


@dataclass
class Point:
    """A labeled point in the figure."""
    label: str
    x: Optional[float] = None
    y: Optional[float] = None
    on_circle: Optional[str] = None  # Circle center label if on a circle
    description: Optional[str] = None


@dataclass
class Line:
    """A line segment or ray."""
    start: str  # Point label
    end: str    # Point label
    style: str = "solid"  # solid, dashed, dotted
    label: Optional[str] = None
    is_ray: bool = False
    is_extended: bool = False


@dataclass
class Circle:
    """A circle with center and radius."""
    center: str  # Point label
    radius: Optional[float] = None
    radius_label: Optional[str] = None
    points_on_circle: List[str] = field(default_factory=list)


@dataclass  
class Angle:
    """An angle with optional marking."""
    vertex: str  # Point label
    ray1_end: str  # Point label for first ray
    ray2_end: str  # Point label for second ray
    value: Optional[str] = None  # e.g., "32°", "x", "2x+10"
    marked: bool = False
    arc_style: str = "single"  # single, double, triple


@dataclass
class Triangle:
    """A triangle defined by three vertices."""
    vertices: Tuple[str, str, str]
    inscribed_in: Optional[str] = None  # Circle center if inscribed
    circumscribed_around: Optional[str] = None
    style: str = "solid"


@dataclass
class Quadrilateral:
    """A quadrilateral defined by four vertices."""
    vertices: Tuple[str, str, str, str]
    is_cyclic: bool = False
    inscribed_in: Optional[str] = None


@dataclass
class Tangent:
    """A tangent line to a circle."""
    circle_center: str
    point_of_tangency: str
    external_point: Optional[str] = None
    label: Optional[str] = None


@dataclass
class Arc:
    """An arc of a circle."""
    circle_center: str
    start_point: str
    end_point: str
    label: Optional[str] = None
    is_major: bool = False


@dataclass
class GeometryFigure:
    """Complete geometry figure with all elements."""
    
    figure_type: FigureType
    description: str
    
    # Elements
    points: List[Point] = field(default_factory=list)
    lines: List[Line] = field(default_factory=list)
    circles: List[Circle] = field(default_factory=list)
    angles: List[Angle] = field(default_factory=list)
    triangles: List[Triangle] = field(default_factory=list)
    quadrilaterals: List[Quadrilateral] = field(default_factory=list)
    tangents: List[Tangent] = field(default_factory=list)
    arcs: List[Arc] = field(default_factory=list)
    
    # Metadata
    given_values: Dict[str, str] = field(default_factory=dict)
    find_values: List[str] = field(default_factory=list)
    
    # Optional pre-rendered image
    image_ref: Optional[str] = None
    
    # Raw data for custom rendering
    raw_yaml: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['figure_type'] = self.figure_type.value
        return result
    
    def get_all_point_labels(self) -> List[str]:
        """Get all point labels used in the figure."""
        labels = set()
        for p in self.points:
            labels.add(p.label)
        for line in self.lines:
            labels.add(line.start)
            labels.add(line.end)
        for circle in self.circles:
            labels.add(circle.center)
            labels.update(circle.points_on_circle)
        for angle in self.angles:
            labels.add(angle.vertex)
            labels.add(angle.ray1_end)
            labels.add(angle.ray2_end)
        for tri in self.triangles:
            labels.update(tri.vertices)
        for quad in self.quadrilaterals:
            labels.update(quad.vertices)
        for tangent in self.tangents:
            labels.add(tangent.circle_center)
            labels.add(tangent.point_of_tangency)
            if tangent.external_point:
                labels.add(tangent.external_point)
        return sorted(list(labels))


class FigureParser:
    """Parse [FIGURE]...[/FIGURE] blocks from question text."""
    
    FIGURE_BLOCK_PATTERN = re.compile(
        r'\[FIGURE\](.*?)\[/FIGURE\]',
        re.DOTALL | re.IGNORECASE
    )
    
    def __init__(self):
        self.figure_type_map = {ft.value: ft for ft in FigureType}
    
    def extract_figure_blocks(self, text: str) -> List[str]:
        """Extract all [FIGURE] blocks from text."""
        matches = self.FIGURE_BLOCK_PATTERN.findall(text)
        return [m.strip() for m in matches]
    
    def _normalize_yaml_block(self, block: str) -> str:
        """
        Normalize YAML block indentation for parsing.
        
        Handles figure blocks that are indented in question bank files.
        The extraction often strips the leading newline/whitespace from the first line
        while keeping subsequent lines indented, creating invalid YAML.
        """
        lines = block.split('\n')
        if len(lines) <= 1:
            return block
        
        # Check if first line has no indent but subsequent lines do
        # This happens when .strip() is called on the extracted block
        first_non_empty_idx = -1
        for i, line in enumerate(lines):
            if line.strip():
                first_non_empty_idx = i
                break
        
        if first_non_empty_idx < 0:
            return block
        
        first_line = lines[first_non_empty_idx]
        first_indent = len(first_line) - len(first_line.lstrip())
        
        # Find the minimum indent of lines AFTER the first non-empty line
        min_subsequent_indent = float('inf')
        for i, line in enumerate(lines):
            if i <= first_non_empty_idx:
                continue
            stripped = line.lstrip()
            if stripped:  # Non-empty line
                indent = len(line) - len(stripped)
                if indent < min_subsequent_indent:
                    min_subsequent_indent = indent
        
        # If first line has no indent but subsequent lines do, 
        # strip the common indent from subsequent lines to align with first
        if first_indent == 0 and min_subsequent_indent > 0 and min_subsequent_indent != float('inf'):
            normalized_lines = []
            for i, line in enumerate(lines):
                if i <= first_non_empty_idx:
                    normalized_lines.append(line)
                elif line.strip():  # Non-empty subsequent line
                    if len(line) >= min_subsequent_indent:
                        normalized_lines.append(line[min_subsequent_indent:])
                    else:
                        normalized_lines.append(line.lstrip())
                else:
                    normalized_lines.append('')
            return '\n'.join(normalized_lines)
        
        # Otherwise, use standard dedent approach
        if first_indent > 0:
            normalized_lines = []
            for line in lines:
                if line.strip():
                    if len(line) >= first_indent:
                        normalized_lines.append(line[first_indent:])
                    else:
                        normalized_lines.append(line.lstrip())
                else:
                    normalized_lines.append('')
            return '\n'.join(normalized_lines)
        
        return block
    
    def parse(self, figure_block: str) -> GeometryFigure:
        """
        Parse a figure block (content between [FIGURE] and [/FIGURE]).
        
        Supports both YAML-structured format and simple key-value format.
        """
        # Normalize indentation - figure blocks from question banks may be indented
        normalized_block = self._normalize_yaml_block(figure_block)
        
        # Try YAML parsing first
        try:
            data = yaml.safe_load(normalized_block)
            if isinstance(data, dict):
                return self._parse_yaml_format(data)
        except yaml.YAMLError:
            pass
        
        # Fallback to simple key-value parsing
        return self._parse_simple_format(normalized_block)
    
    def _parse_yaml_format(self, data: Dict) -> GeometryFigure:
        """Parse YAML-structured figure data."""
        
        # Determine figure type
        type_str = data.get('type', 'generic')
        subtype = data.get('subtype', '')
        
        if subtype:
            full_type = f"{type_str}_{subtype}" if '_' not in subtype else subtype
        else:
            full_type = type_str
            
        figure_type = self.figure_type_map.get(full_type, FigureType.GENERIC)
        
        # Get description
        description = data.get('description', '')
        
        # Create figure
        figure = GeometryFigure(
            figure_type=figure_type,
            description=description,
            raw_yaml=data
        )
        
        # Parse elements
        elements = data.get('elements', [])
        for elem in elements:
            self._parse_element(elem, figure)
        
        # Parse given/find values
        figure.given_values = data.get('given_values', {})
        if 'given_angles' in data:
            figure.given_values.update(data['given_angles'])
        figure.find_values = data.get('find_values', data.get('find_angles', []))
        
        # Image reference
        figure.image_ref = data.get('image_ref')
        
        return figure
    
    def _parse_element(self, elem: Dict, figure: GeometryFigure):
        """Parse a single element and add to figure."""
        
        if 'circle' in elem:
            circle_data = elem['circle']
            circle = Circle(
                center=circle_data.get('center', 'O'),
                radius=circle_data.get('radius'),
                radius_label=circle_data.get('radius_label'),
                points_on_circle=circle_data.get('points', [])
            )
            figure.circles.append(circle)
            
        elif 'triangle' in elem:
            tri_data = elem['triangle']
            vertices = tri_data.get('vertices', ['A', 'B', 'C'])
            triangle = Triangle(
                vertices=tuple(vertices[:3]) if len(vertices) >= 3 else ('A', 'B', 'C'),
                inscribed_in=tri_data.get('inscribed_in'),
                circumscribed_around=tri_data.get('circumscribed_around'),
                style=tri_data.get('style', 'solid')
            )
            figure.triangles.append(triangle)
            
        elif 'quadrilateral' in elem:
            quad_data = elem['quadrilateral']
            vertices = quad_data.get('vertices', ['A', 'B', 'C', 'D'])
            quad = Quadrilateral(
                vertices=tuple(vertices[:4]) if len(vertices) >= 4 else ('A', 'B', 'C', 'D'),
                is_cyclic=quad_data.get('cyclic', False),
                inscribed_in=quad_data.get('inscribed_in')
            )
            figure.quadrilaterals.append(quad)
            
        elif 'tangent' in elem:
            tan_data = elem['tangent']
            tangent = Tangent(
                circle_center=tan_data.get('circle', 'O'),
                point_of_tangency=tan_data.get('point', 'T'),
                external_point=tan_data.get('external_point'),
                label=tan_data.get('label')
            )
            figure.tangents.append(tangent)
            
        elif 'angle' in elem:
            angle_data = elem['angle']
            vertex = angle_data.get('vertex', 'A')
            rays = angle_data.get('rays', ['B', 'C'])
            angle = Angle(
                vertex=vertex,
                ray1_end=rays[0] if len(rays) > 0 else 'B',
                ray2_end=rays[1] if len(rays) > 1 else 'C',
                value=angle_data.get('value'),
                marked=angle_data.get('marked', False),
                arc_style=angle_data.get('arc_style', 'single')
            )
            figure.angles.append(angle)
            
        elif 'line' in elem:
            line_data = elem['line']
            points = line_data.get('points', ['A', 'B'])
            line = Line(
                start=points[0] if len(points) > 0 else 'A',
                end=points[1] if len(points) > 1 else 'B',
                style=line_data.get('style', 'solid'),
                label=line_data.get('label'),
                is_ray=line_data.get('is_ray', False),
                is_extended=line_data.get('extended', False)
            )
            figure.lines.append(line)
            
        elif 'point' in elem:
            point_data = elem['point']
            point = Point(
                label=point_data.get('label', 'P'),
                x=point_data.get('x'),
                y=point_data.get('y'),
                on_circle=point_data.get('on_circle'),
                description=point_data.get('description')
            )
            figure.points.append(point)
    
    def _parse_simple_format(self, text: str) -> GeometryFigure:
        """Parse simple key-value format."""
        
        lines = text.strip().split('\n')
        data = {}
        current_key = None
        current_value = []
        
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith(' '):
                # Save previous key-value
                if current_key:
                    data[current_key] = '\n'.join(current_value).strip()
                
                # Parse new key-value
                key, _, value = line.partition(':')
                current_key = key.strip().lower().replace(' ', '_')
                current_value = [value.strip()] if value.strip() else []
            elif current_key:
                current_value.append(line)
        
        # Save last key-value
        if current_key:
            data[current_key] = '\n'.join(current_value).strip()
        
        # Build figure from simple data
        type_str = data.get('type', 'generic')
        figure_type = self.figure_type_map.get(type_str, FigureType.GENERIC)
        
        return GeometryFigure(
            figure_type=figure_type,
            description=data.get('description', ''),
            image_ref=data.get('image_ref'),
            raw_yaml=data
        )
    
    def parse_from_question(self, question_text: str) -> Optional[GeometryFigure]:
        """
        Extract and parse figure from a full question text.
        
        Returns None if no figure block found.
        """
        blocks = self.extract_figure_blocks(question_text)
        if blocks:
            return self.parse(blocks[0])
        return None


class FigureValidator:
    """Validate geometry figures for completeness and consistency."""
    
    def validate(self, figure: GeometryFigure) -> Tuple[bool, List[str]]:
        """
        Validate a figure for completeness and consistency.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # 1. Check description
        if not figure.description:
            issues.append("Missing figure description")
        
        # 2. Check for duplicate point definitions
        defined_labels = set()
        for p in figure.points:
            if p.label in defined_labels:
                issues.append(f"Duplicate definition for point '{p.label}'")
            else:
                defined_labels.add(p.label)
        
        # 3. Check for referenced points (structural elements)
        structural_labels = set(p.label for p in figure.points)
        for line in figure.lines:
            structural_labels.add(line.start)
            structural_labels.add(line.end)
        for circle in figure.circles:
            structural_labels.add(circle.center)
            structural_labels.update(circle.points_on_circle)
        for tri in figure.triangles:
            structural_labels.update(tri.vertices)
        for quad in figure.quadrilaterals:
            structural_labels.update(quad.vertices)
        for tangent in figure.tangents:
            structural_labels.add(tangent.circle_center)
            structural_labels.add(tangent.point_of_tangency)
            if tangent.external_point:
                structural_labels.add(tangent.external_point)

        # 4. Validate lines
        for line in figure.lines:
            if line.start == line.end:
                issues.append(f"Line has same start and end point '{line.start}'")

        # 5. Validate triangles
        for tri in figure.triangles:
            if len(set(tri.vertices)) < 3:
                issues.append(f"Triangle {tri.vertices} must have 3 distinct vertices")

        # 6. Validate quadrilaterals
        for quad in figure.quadrilaterals:
            if len(set(quad.vertices)) < 4:
                issues.append(f"Quadrilateral {quad.vertices} must have 4 distinct vertices")
        
        # 7. Check angles have valid vertices and rays
        for angle in figure.angles:
            if angle.vertex not in structural_labels:
                issues.append(f"Angle vertex '{angle.vertex}' not found in structural elements")
            if angle.ray1_end not in structural_labels:
                issues.append(f"Angle ray end '{angle.ray1_end}' not found in structural elements")
            if angle.ray2_end not in structural_labels:
                issues.append(f"Angle ray end '{angle.ray2_end}' not found in structural elements")
            if angle.vertex == angle.ray1_end or angle.vertex == angle.ray2_end:
                issues.append(f"Angle vertex '{angle.vertex}' cannot be the same as a ray end")
        
        # 8. Check figure type is not generic if structured
        if figure.figure_type == FigureType.GENERIC:
            if figure.circles or figure.triangles or figure.tangents or figure.quadrilaterals:
                issues.append("Figure has elements but type is 'generic' - consider specifying type")
        
        return len(issues) == 0, issues


# ============================================================================
# Figure Templates for Common ICSE Geometry Questions
# ============================================================================

FIGURE_TEMPLATES = {
    "circle_inscribed_triangle": {
        "type": "circle_inscribed_angle",
        "description": "Circle with center O and inscribed triangle ABC",
        "elements": [
            {"circle": {"center": "O", "points": ["A", "B", "C"]}},
            {"triangle": {"vertices": ["A", "B", "C"], "inscribed_in": "O"}}
        ]
    },
    
    "tangent_from_external_point": {
        "type": "circle_tangent",
        "description": "Circle with center O, tangent PT from external point P",
        "elements": [
            {"circle": {"center": "O"}},
            {"tangent": {"circle": "O", "point": "T", "external_point": "P"}},
            {"line": {"points": ["P", "T"], "label": "PT"}}
        ]
    },
    
    "two_tangents_external": {
        "type": "circle_tangent",
        "description": "Two tangents PA and PB from external point P to circle with center O",
        "elements": [
            {"circle": {"center": "O"}},
            {"tangent": {"circle": "O", "point": "A", "external_point": "P"}},
            {"tangent": {"circle": "O", "point": "B", "external_point": "P"}},
            {"line": {"points": ["P", "A"]}},
            {"line": {"points": ["P", "B"]}}
        ]
    },
    
    "cyclic_quadrilateral": {
        "type": "cyclic_quadrilateral",
        "description": "Cyclic quadrilateral ABCD inscribed in circle with center O",
        "elements": [
            {"circle": {"center": "O", "points": ["A", "B", "C", "D"]}},
            {"quadrilateral": {"vertices": ["A", "B", "C", "D"], "cyclic": True, "inscribed_in": "O"}}
        ]
    },
    
    "similar_triangles_bpt": {
        "type": "bpt_triangle",
        "description": "Triangle ABC with DE parallel to BC, where D is on AB and E is on AC",
        "elements": [
            {"triangle": {"vertices": ["A", "B", "C"]}},
            {"point": {"label": "D", "description": "on AB"}},
            {"point": {"label": "E", "description": "on AC"}},
            {"line": {"points": ["D", "E"], "style": "solid"}}
        ]
    },
    
    "alternate_segment": {
        "type": "alternate_segment",
        "description": "Circle with tangent at point T and chord through T",
        "elements": [
            {"circle": {"center": "O", "points": ["T", "A", "B"]}},
            {"tangent": {"circle": "O", "point": "T", "external_point": "P"}},
            {"line": {"points": ["T", "A"], "label": "chord TA"}}
        ]
    }
}


def get_template(template_name: str) -> Optional[Dict]:
    """Get a predefined figure template by name."""
    return FIGURE_TEMPLATES.get(template_name)


def list_templates() -> List[str]:
    """List all available figure template names."""
    return list(FIGURE_TEMPLATES.keys())


# ============================================================================
# Testing
# ============================================================================

def test():
    """Test the figure parsing functionality."""
    
    print("=" * 60)
    print("Testing Geometry Schema Module")
    print("=" * 60)
    
    # Test 1: Parse YAML format
    yaml_block = """
type: circle_theorem
subtype: tangent
description: Circle with center O, tangent PT at T, chord TA
elements:
  - circle:
      center: O
      radius: 3cm
      points: [T, A, B]
  - tangent:
      circle: O
      point: T
      external_point: P
  - angle:
      vertex: T
      rays: [A, P]
      value: "32°"
      marked: true
given_angles:
  PTA: "32°"
find_angles: [TAB, TBA]
"""
    
    parser = FigureParser()
    figure = parser.parse(yaml_block)
    
    print("\n1. YAML Format Parsing:")
    print(f"   Type: {figure.figure_type.value}")
    print(f"   Description: {figure.description}")
    print(f"   Circles: {len(figure.circles)}")
    print(f"   Tangents: {len(figure.tangents)}")
    print(f"   Angles: {len(figure.angles)}")
    print(f"   Given values: {figure.given_values}")
    print(f"   Find values: {figure.find_values}")
    print(f"   All points: {figure.get_all_point_labels()}")
    
    # Test 2: Parse simple format
    simple_block = """
type: similar_triangles
description: |
    Triangle ABC with D on AB, E on AC.
    DE is parallel to BC.
    AD = 3cm, DB = 5cm, AE = 4cm
image_ref: figures/bpt_example.png
"""
    
    figure2 = parser.parse(simple_block)
    
    print("\n2. Simple Format Parsing:")
    print(f"   Type: {figure2.figure_type.value}")
    print(f"   Description: {figure2.description[:50]}...")
    print(f"   Image ref: {figure2.image_ref}")
    
    # Test 3: Extract from full question
    question_text = """
Q5 [4 marks] (medium)

    In the given figure, O is the center of the circle. PT is a tangent at T.
    If ∠TAB = 32°, find: (i) ∠TPA (ii) ∠TBA
    
    [FIGURE]
    type: circle_tangent
    description: Circle with center O, tangent PT at T, chord TA, point B on circle
    elements:
      - circle: {center: O, points: [T, A, B]}
      - tangent: {circle: O, point: T, external_point: P}
    [/FIGURE]
    
    Subtopic: Alternate Segment Theorem
    [Source: ICSE 2024]
"""
    
    figure3 = parser.parse_from_question(question_text)
    
    print("\n3. Extract from Question:")
    print(f"   Found figure: {figure3 is not None}")
    if figure3:
        print(f"   Type: {figure3.figure_type.value}")
        print(f"   Description: {figure3.description[:50]}...")
    
    # Test 4: Validation
    validator = FigureValidator()
    is_valid, issues = validator.validate(figure)
    
    print("\n4. Validation:")
    print(f"   Valid: {is_valid}")
    if issues:
        print(f"   Issues: {issues}")
    
    # Test 5: Templates
    print("\n5. Available Templates:")
    for name in list_templates():
        print(f"   - {name}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test()
