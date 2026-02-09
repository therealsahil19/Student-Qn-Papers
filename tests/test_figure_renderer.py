import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_extractor.geometry_schema import FigureParser
from question_extractor.figure_renderer import FigureRenderer

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

def test(output_dir: str = "./test_figures"):
    """Test figure rendering with sample figures."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot run tests: matplotlib not installed")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Testing Figure Renderer")
    print("=" * 60)
    
    parser = FigureParser()
    renderer = FigureRenderer()
    
    # Test 1: Circle with inscribed triangle
    print("\n1. Rendering: Circle with inscribed triangle")
    
    figure_yaml = """
type: circle_inscribed_angle
description: Circle with center O and inscribed triangle ABC
elements:
  - circle:
      center: O
      radius: 3
      points: [A, B, C]
  - triangle:
      vertices: [A, B, C]
      inscribed_in: O
  - angle:
      vertex: A
      rays: [B, C]
      value: "50°"
      marked: true
"""
    
    figure = parser.parse(figure_yaml)
    renderer.render(figure)
    renderer.save_png(str(output_path / "test_inscribed_triangle.png"))
    renderer.close()
    print(f"   Saved: {output_path / 'test_inscribed_triangle.png'}")
    
    # Test 2: Tangent from external point
    print("\n2. Rendering: Tangent from external point")
    
    figure_yaml = """
type: circle_tangent
description: Circle with tangent PT from external point P
elements:
  - circle:
      center: O
      radius: 2.5
      points: [T]
  - tangent:
      circle: O
      point: T
      external_point: P
  - line:
      points: [O, T]
      style: dashed
"""
    
    figure = parser.parse(figure_yaml)
    renderer.render(figure)
    renderer.save_png(str(output_path / "test_tangent.png"))
    renderer.close()
    print(f"   Saved: {output_path / 'test_tangent.png'}")
    
    # Test 3: Cyclic quadrilateral
    print("\n3. Rendering: Cyclic quadrilateral")
    
    figure_yaml = """
type: cyclic_quadrilateral
description: Cyclic quadrilateral ABCD inscribed in circle
elements:
  - circle:
      center: O
      radius: 3
      points: [A, B, C, D]
  - quadrilateral:
      vertices: [A, B, C, D]
      cyclic: true
      inscribed_in: O
  - angle:
      vertex: A
      rays: [D, B]
      value: "80°"
      marked: true
  - angle:
      vertex: C
      rays: [B, D]
      value: "100°"
      marked: true
"""
    
    figure = parser.parse(figure_yaml)
    renderer.render(figure)
    renderer.save_png(str(output_path / "test_cyclic_quad.png"))
    renderer.close()
    print(f"   Saved: {output_path / 'test_cyclic_quad.png'}")
    
    # Test 4: Similar triangles (BPT)
    print("\n4. Rendering: Similar triangles (BPT)")
    
    figure_yaml = """
type: bpt_triangle
description: Triangle ABC with DE parallel to BC
elements:
  - triangle:
      vertices: [A, B, C]
  - point:
      label: D
      x: -1.5
      y: 0.75
  - point:
      label: E
      x: 1.5
      y: 0.75
  - line:
      points: [D, E]
      style: solid
"""
    
    figure = parser.parse(figure_yaml)
    renderer.render(figure)
    renderer.save_png(str(output_path / "test_bpt.png"))
    renderer.close()
    print(f"   Saved: {output_path / 'test_bpt.png'}")
    
    print("\n" + "=" * 60)
    print(f"All test figures saved to: {output_path.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
        test(output_dir)
    else:
        test()
