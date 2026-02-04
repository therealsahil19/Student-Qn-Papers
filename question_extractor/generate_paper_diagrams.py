
import os
import sys
import math
from pathlib import Path

# Add the current directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geometry_schema import FigureParser
from figure_renderer import FigureRenderer

def generate_diagrams():
    parser = FigureParser()
    renderer = FigureRenderer()
    
    # Ensure images directory exists
    output_dir = Path("C:/Users/mehna/OneDrive/Desktop/Student Qn papers/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    diagrams = {
        "q2": """
type: circle_tangent
description: PA, PB tangents. ∠AOB = 110°.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 3}
  - point: {label: A, x: -1.03, y: 2.82}
  - point: {label: B, x: -1.03, y: -2.82}
  - point: {label: P, x: 7.2, y: 0}
  - line: {points: [P, A]}
  - line: {points: [P, B]}
  - line: {points: [O, A], style: dashed}
  - line: {points: [O, B], style: dashed}
  - angle: {vertex: O, rays: [A, B], value: "110°", marked: true}
""",
        "q12": """
type: circle_tangent
description: PA, PB tangents. ∠APB = 60°.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 3}
  - point: {label: P, x: 6, y: 0}
  - point: {label: A, x: 1.5, y: 2.598}
  - point: {label: B, x: 1.5, y: -2.598}
  - line: {points: [P, A]}
  - line: {points: [P, B]}
  - line: {points: [A, B]}
  - line: {points: [O, A], style: dashed}
  - line: {points: [O, B], style: dashed}
  - angle: {vertex: P, rays: [A, B], value: "60°", marked: true}
""",
        "q16": """
type: cyclic_quadrilateral
description: ABCD cyclic. ∠EBF = 130°.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 4}
  - point: {label: B, x: 0, y: 4}
  - point: {label: A, x: -3.06, y: 2.57}
  - point: {label: C, x: 3.06, y: 2.57}
  - point: {label: D, x: 0, y: -4}
  - quadrilateral: {vertices: [A, B, C, D], cyclic: true, inscribed_in: O}
  - point: {label: F, x: 2, y: 5.2}
  - point: {label: E, x: -2, y: 5.2}
  - line: {points: [B, F]}
  - line: {points: [B, E]}
  - angle: {vertex: B, rays: [F, E], value: "130°", marked: true}
""",
        "q18": """
type: circle_secant
description: Chord AB (not diameter) and CD intersect at P outside. Dotted perpendicular from O to CD.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 6}
  - point: {label: P, x: 11, y: 0}
  - point: {label: B, x: 5.37, y: 2.68}
  - point: {label: A, x: -4.3, y: 4.17}
  - line: {points: [P, A]}
  - point: {label: D, x: 5.92, y: -1.0}
  - point: {label: C, x: -2.85, y: -5.28}
  - line: {points: [P, C]}
  - point: {label: " ", x: 0.9, y: -2.85}
  - line: {points: [O, " "], style: dotted}
""",
        "q21": """
type: circle_tangent
description: PT tangent, PAB secant. CD || PT. CD meets AB at E.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 3}
  - point: {label: T, x: 0, y: 3}
  - point: {label: P, x: -8, y: 3}
  - line: {points: [P, T]}
  - point: {label: B, x: -3, y: 0}
  - point: {label: A, x: 1.41, y: -2.65}
  - line: {points: [P, A]}
  - point: {label: C, x: -2.6, y: 1.5}
  - point: {label: D, x: 2.6, y: 1.5}
  - line: {points: [C, D]}
  - point: {label: E, x: -5.5, y: 1.5}
""",
        "q24a": """
type: generic
description: Two intersecting circles. ACD line through C.
elements:
  - point: {label: P, x: -2.5, y: 0}
  - point: {label: Q, x: 2.5, y: 0}
  - circle: {center: P, radius: 3}
  - circle: {center: Q, radius: 3}
  - point: {label: B, x: 0, y: 1.66}
  - point: {label: C, x: 0, y: -1.66}
  - point: {label: A, x: -4.5, y: -3.2}
  - point: {label: D, x: 4.5, y: -0.1}
  - line: {points: [A, D]}
  - line: {points: [P, B], style: dashed}
  - line: {points: [Q, B], style: dashed}
  - angle: {vertex: P, rays: [A, B], value: "130°", marked: true}
""",
        "q25b": """
type: circle_tangent
description: AB diameter. CD tangent at D. EB || CD.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 3}
  - point: {label: A, x: -3, y: 0}
  - point: {label: B, x: 3, y: 0}
  - line: {points: [A, B]}
  - point: {label: D, x: 1.5, y: 2.6}
  - point: {label: C, x: 6, y: 0}
  - line: {points: [C, D]}
  - point: {label: E, x: -1.5, y: 2.6}
  - line: {points: [E, B]}
  - angle: {vertex: B, rays: [E, D], value: "35°", marked: true}
""",
        "q26a": """
type: cyclic_quadrilateral
description: PQRS cyclic. PS produced to T.
elements:
  - point: {label: O, x: 0, y: 0}
  - circle: {center: O, radius: 4}
  - point: {label: P, x: -1.5, y: 3.7}
  - point: {label: Q, x: 3.7, y: 1.5}
  - point: {label: R, x: 2, y: -3.5}
  - point: {label: S, x: -3, y: -2.6}
  - quadrilateral: {vertices: [P, Q, R, S], cyclic: true, inscribed_in: O}
  - point: {label: T, x: -6, y: -5}
  - line: {points: [S, T]}
  - point: {label: O2, x: -1, y: -1}
  - circle: {center: O2, radius: 3.0}
  - point: {label: M, x: -4, y: -3.5}
  - point: {label: N, x: 1.5, y: 1}
  - line: {points: [M, N]}
""",
    }

    for name, block in diagrams.items():
        print(f"Generating {name}...")
        try:
            figure = parser.parse(block)
            renderer.render(figure)
            output_path = output_dir / f"{name}.svg"
            renderer.save_svg(str(output_path))
            renderer.close()
        except Exception as e:
            print(f"Error generating {name}: {e}")

if __name__ == "__main__":
    generate_diagrams()
