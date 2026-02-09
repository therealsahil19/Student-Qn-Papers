import sys
import os
from pathlib import Path

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from question_extractor.geometry_schema import FigureParser
from question_extractor.figure_renderer import FigureRenderer
from question_extractor.diagram_utils import ensure_output_directory, create_diagram

# Q17: Parallelogram GUNS. GS || UN, GU || SN.
# GS=3x, UN=18 (so x=6)
# SN=26, GU=3y-1 (so y=9)
q17_yaml = """
type: generic
description: Parallelogram GUNS
elements:
  - point: {label: G, x: 0, y: 0}
  - point: {label: U, x: 18, y: 0}
  - point: {label: N, x: 23, y: 10}
  - point: {label: S, x: 5, y: 10}
  - quadrilateral: {vertices: [G, U, N, S]}
  - line: {points: [G, S], label: "3x"}
  - line: {points: [U, N], label: "18"}
  - line: {points: [G, U], label: "3y-1"}
  - line: {points: [S, N], label: "26"}
"""

# Q19: Rhombus ABCD, ∠BAD = 70°. BD produced to E, BD = DE.
# B(5,0), D(1.71, 4.7) => Vector BD = (-3.29, 4.7)
# E = D + Vector BD = (1.71 - 3.29, 4.7 + 4.7) = (-1.58, 9.4)
q19_yaml = """
type: generic
description: Rhombus ABCD with diagonal BD produced to E
elements:
  - point: {label: A, x: 0, y: 0}
  - point: {label: B, x: 5, y: 0}
  - point: {label: C, x: 6.71, y: 4.7}
  - point: {label: D, x: 1.71, y: 4.7}
  - point: {label: E, x: -1.58, y: 9.4}
  - quadrilateral: {vertices: [A, B, C, D]}
  - line: {points: [B, E], style: dashed}
  - line: {points: [C, E]}
  - angle: {vertex: A, rays: [B, D], value: "70°", marked: true}
"""

# Q21: Quadrilateral ABCD, bisectors of A and B meet at P.
q21_yaml = """
type: generic
description: Quadrilateral ABCD with angle bisectors of A and B meeting at P
elements:
  - point: {label: A, x: 0, y: 0}
  - point: {label: B, x: 8, y: 0}
  - point: {label: C, x: 7, y: 6}
  - point: {label: D, x: 1, y: 5}
  - quadrilateral: {vertices: [A, B, C, D]}
  - point: {label: P, x: 4, y: 2}
  - line: {points: [A, P], style: dashed}
  - line: {points: [B, P], style: dashed}
  - angle: {vertex: C, value: "100°", marked: false}
  - angle: {vertex: D, value: "50°", marked: false}
"""

# Q24a: Parallelograms ABCD (top) and ABEF (bottom) on base AB.
# D(6,4), C(11,4), B(5,0), A(0,0).
# E(2,-4), F(-3,-4).
# Line DE intersects AB at P and BC at Q.
q24a_yaml = """
type: generic
description: Parallelograms ABCD and ABEF on opposite sides of base AB
elements:
  - point: {label: A, x: 0, y: 0}
  - point: {label: B, x: 5, y: 0}
  - point: {label: C, x: 11, y: 4}
  - point: {label: D, x: 6, y: 4}
  - point: {label: E, x: 2, y: -4}
  - point: {label: F, x: -3, y: -4}
  - quadrilateral: {vertices: [A, B, C, D]}
  - quadrilateral: {vertices: [A, B, E, F]}
  - line: {points: [D, E], style: solid}
  - point: {label: P, description: "intersection of AB and DE"}
  - point: {label: Q, description: "intersection of BC and DE"}
"""

# Q26b: Overlapping parallelograms RISK and CLUE.
q26b_yaml = """
type: generic
description: Overlapping parallelograms RISK and CLUE
elements:
  - point: {label: R, x: 0, y: 0}
  - point: {label: I, x: 6, y: 0}
  - point: {label: S, x: 8, y: 3}
  - point: {label: K, x: 2, y: 3}
  - point: {label: C, x: 3, y: 0}
  - point: {label: L, x: 9, y: 0}
  - point: {label: U, x: 11, y: 3}
  - point: {label: E, x: 5, y: 3}
  - quadrilateral: {vertices: [R, I, S, K]}
  - quadrilateral: {vertices: [C, L, U, E]}
  - point: {label: X, description: "intersection of SK and CE"}
  - angle: {vertex: K, rays: [R, S], value: "120°", marked: true}
  - angle: {vertex: L, rays: [C, U], value: "70°", marked: true}
"""

output_dir = ensure_output_directory("images")
create_diagram("q17", q17_yaml, output_dir)
create_diagram("q19", q19_yaml, output_dir)
create_diagram("q21", q21_yaml, output_dir)
create_diagram("q24a", q24a_yaml, output_dir)
create_diagram("q26b", q26b_yaml, output_dir)
