import os
import sys
import math
from pathlib import Path

# Add the question_extractor directory to the path so we can import the modules
sys.path.append(os.path.join(os.getcwd(), 'question_extractor'))

from geometry_schema import FigureParser
from figure_renderer import FigureRenderer

def generate_q21():
    parser = FigureParser()
    renderer = FigureRenderer()
    
    # Ensure images directory exists
    output_dir = Path("C:/Users/mehna/OneDrive/Desktop/Student Qn papers/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Coordinates calculation for Q21:
    # O is (0,0), radius R=100
    # A is at 0 degrees -> (100, 0)
    # E is at 150 degrees -> (100*cos(150), 100*sin(150)) = (-86.6, 50)
    # Angle AOD = 78 degrees -> D is at 78 degrees -> (100*cos(78), 100*sin(78)) = (20.8, 97.8)
    # B and C are points on the circle such that ABCD or ABED is cyclic
    # Usually in these problems, B and C are on the major arc AE.
    # Let's place B and C to form a nice cyclic quad ABED
    # B at 220 degrees -> (-76.6, -64.3)
    # C at 280 degrees -> (17.4, -98.5)
    
    block = """
type: circle_inscribed_angle
description: Circle with center O, angles AOE=150 and DAO=51. Find BEC and EBC.
elements:
  - circle: {center: O, radius: 100, points: [A, B, C, D, E]}
  - point: {label: O, x: 0, y: 0}
  - point: {label: A, x: 100, y: 0}
  - point: {label: E, x: -86.6, y: 50}
  - point: {label: D, x: 20.8, y: 97.8}
  - point: {label: B, x: -76.6, y: -64.3}
  - point: {label: C, x: 17.4, y: -98.5}
  - line: {points: [O, A], style: dashed}
  - line: {points: [O, E], style: dashed}
  - line: {points: [O, D], style: dashed}
  - line: {points: [A, B]}
  - line: {points: [B, E]}
  - line: {points: [E, D]}
  - line: {points: [D, A]}
  - line: {points: [B, C]}
  - line: {points: [E, C]}
  - angle: {vertex: O, rays: [A, E], value: "150°", marked: true}
  - angle: {vertex: A, rays: [D, O], value: "51°", marked: true}
"""

    print("Generating q21 diagram...")
    try:
        figure = parser.parse(block)
        renderer.render(figure)
        output_path = output_dir / "q21.svg"
        renderer.save_svg(str(output_path))
        renderer.close()
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error generating q21: {e}")

if __name__ == "__main__":
    generate_q21()
