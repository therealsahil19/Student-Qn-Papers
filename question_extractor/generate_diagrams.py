import os
import sys
import math
from pathlib import Path

# Add the current directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from question_extractor.geometry_schema import FigureParser
from question_extractor.figure_renderer import FigureRenderer
from question_extractor.diagram_utils import ensure_output_directory, create_diagram

def generate_diagrams():
    # Use relative path or environment variable, fallback to default
    output_path_str = os.environ.get("DIAGRAM_OUTPUT_DIR", "images")
    # If the script is run from the root, 'images' is fine. 
    # If run from question_extractor, we might want to go up one level.
    # However, 'images' relative to CWD is usually best for scripts.
    # The original was absolute: "C:/Users/mehna/OneDrive/Desktop/Student Qn papers/images"
    # We will use "images" in the current working directory.
    
    output_dir = ensure_output_directory(output_path_str)
    
    renderer = FigureRenderer()

    # Helper for heights and distances math
    # Q12: Cliff 80m, Tower h. Angles 60 and 45.
    d_q12 = 80 / math.tan(math.radians(60)) # 46.18
    h_q12 = 80 - d_q12 * math.tan(math.radians(45)) # 33.82
    
    # Q18b: Lighthouse 100m. Angles 48 and 35 on opposite sides.
    d1_q18b = 100 / math.tan(math.radians(48))
    d2_q18b = 100 / math.tan(math.radians(35))

    diagrams = {
        "q10": """
type: similar_triangles
description: Triangle ABC with XY parallel to BC, ratio 3:4
elements:
  - point: {label: A, x: 0, y: 7}
  - point: {label: B, x: -3.5, y: 0}
  - point: {label: C, x: 3.5, y: 0}
  - triangle: {vertices: [A, B, C]}
  - point: {label: X, description: "on AB ratio 3:4"}
  - point: {label: Y, description: "on AC ratio 3:4"}
  - line: {points: [X, Y], style: solid}
""",
        "q14": """
type: right_triangle
description: Right triangle ABC with altitude BD
elements:
  - point: {label: B, x: 0, y: 0}
  - point: {label: A, x: 0, y: 4}
  - point: {label: C, x: 3, y: 0}
  - triangle: {vertices: [A, B, C]}
  - point: {label: D, description: "altitude from B to AC"}
  - line: {points: [B, D], style: solid}
""",
        "q15": """
type: circle_chord
description: Two chords AB and CD intersect at P. AP=2, PB=8, CP=4, PD=4.
elements:
  - circle: {center: O, radius: 5}
  - point: {label: A, x: -5, y: 0}
  - point: {label: B, x: 5, y: 0}
  - point: {label: C, x: -3, y: 4}
  - point: {label: D, x: -3, y: -4}
  - point: {label: P, description: "intersection of AB and CD"}
  - line: {points: [A, B]}
  - line: {points: [C, D]}
""",
        "q16": """
type: trapezium
description: Trapezium ABCD with diagonals intersecting at O
elements:
  - point: {label: D, x: -3, y: 0}
  - point: {label: C, x: 5, y: 0}
  - point: {label: A, x: -1, y: 3}
  - point: {label: B, x: 3, y: 3}
  - quadrilateral: {vertices: [D, C, B, A]}
  - point: {label: O, description: "intersection of AC and BD"}
  - line: {points: [A, C]}
  - line: {points: [B, D]}
""",
    }

    try:
        for name, block in diagrams.items():
            create_diagram(name, block, output_dir, renderer=renderer)
    finally:
        renderer.close()

if __name__ == "__main__":
    generate_diagrams()