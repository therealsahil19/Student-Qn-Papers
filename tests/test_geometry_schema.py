import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_extractor.geometry_schema import FigureParser, FigureValidator, list_templates

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
