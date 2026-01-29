
import sys
import os
import math
from pathlib import Path

# Add question_extractor to path
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir / "question_extractor"))

from geometry_schema import GeometryFigure, FigureType, Point, Line, Circle, Arc, Tangent
from figure_renderer import FigureRenderer, RenderConfig

OUTPUT_DIR = current_dir / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

def create_iron_pole():
    """
    Q24(a): Solid iron pole.
    Perspective: Use filled ellipses to show solid surfaces.
    """
    print("Generating 3D Solid Iron Pole diagram...")
    
    r1 = 1.2
    h1 = 22.0
    r2 = 0.8
    h2 = 6.0
    
    # 3D Cylinder Bases (as ellipses)
    # Drawing order matters for overlap: Bottom to Top
    
    points = [
        Point("B1", 0, 0),
        Point("B2", 0, h1),
        Point("B3", 0, h1 + h2),
        Point("L1", -r1, 0), Point("R1", r1, 0),
        Point("L2", -r1, h1), Point("R2", r1, h1),
        Point("L3", -r2, h1), Point("R3", r2, h1),
        Point("L4", -r2, h1+h2), Point("R4", r2, h1+h2)
    ]
    
    lines = [
        Line("L1", "L2"), Line("R1", "R2"), # Side walls 1
        Line("L3", "L4"), Line("R3", "R4")  # Side walls 2
    ]
    
    # Ellipses with z-order and fill
    ellipses = [
        # Bottom base
        {"center": "B1", "width": 2*r1, "height": 0.4*r1, "zorder": 1}, 
        # Junction surface (Top of bottom cylinder) - FILLED to look solid
        {"center": "B2", "width": 2*r1, "height": 0.4*r1, "fill": True, "zorder": 2}, 
        # Top base - FILLED
        {"center": "B3", "width": 2*r2, "height": 0.4*r2, "fill": True, "zorder": 4}
    ]
    
    figure = GeometryFigure(
        figure_type=FigureType.MENSURATION_COMBINED,
        description="Solid 3D Iron Pole",
        points=points,
        lines=lines,
        raw_yaml={"ellipses": ellipses}
    )
    
    config = RenderConfig(figsize=(6, 12), line_width=2.5, line_color="black", show_points=False, show_labels=False)
    renderer = FigureRenderer(config)
    renderer.render(figure)
    renderer.save_png(str(OUTPUT_DIR / "iron_pole.png"))
    renderer.close()

def create_sphere_in_cylinder():
    """
    Q25(b): Sphere in cylinder.
    """
    print("Generating 3D Sphere in Cylinder diagram...")
    r = 3.0
    h = 2*r
    
    ellipses = [
        {"center": "B", "width": 2*r, "height": 0.6*r}, # Base
        {"center": "T", "width": 2*r, "height": 0.6*r, "style": "dashed"}  # Top water level
    ]
    
    points = [
        Point("B", 0, 0),
        Point("T", 0, h),
        Point("C", 0, r), 
        Point("L1", -r, 0), Point("R1", r, 0),
        Point("L2", -r, h), Point("R2", r, h)
    ]
    
    lines = [
        Line("L1", "L2"), Line("R1", "R2")
    ]
    
    # Sphere filled with light shade or just white to obscure back lines
    circles = [Circle("C", radius=r)]
    # Injected fill for circle
    circles[0].fill = True
    
    figure = GeometryFigure(
        figure_type=FigureType.MENSURATION_COMBINED,
        description="3D Sphere in Cylinder",
        points=points,
        lines=lines,
        circles=circles,
        raw_yaml={"ellipses": ellipses}
    )
    
    config = RenderConfig(figsize=(8, 8), line_width=2.5, show_points=False, show_labels=False)
    renderer = FigureRenderer(config)
    renderer.render(figure)
    renderer.save_png(str(OUTPUT_DIR / "cone_hemisphere.png")) 
    renderer.close()

def create_six_spheres():
    """
    Q25(a): 6 Spheres in Cylinder.
    """
    print("Generating 3D 6 Spheres diagram...")
    r = 1.0
    
    ellipses = [
        {"center": "B", "width": 2*r, "height": 0.5*r},
        {"center": "T", "width": 2*r, "height": 0.5*r}
    ]
    
    points = [
        Point("B", 0, 0), Point("T", 0, 12*r),
        Point("L1", -r, 0), Point("R1", r, 0),
        Point("L2", -r, 12*r), Point("R2", r, 12*r)
    ]
    
    lines = [Line("L1", "L2"), Line("R1", "R2")]
    
    circles = []
    points_c = []
    for i in range(6):
        label = f"S{i}"
        points_c.append(Point(label, 0, r + 2*r*i))
        c = Circle(label, radius=r)
        c.fill = True
        circles.append(c)
        
    figure = GeometryFigure(
        figure_type=FigureType.MENSURATION_COMBINED,
        description="3D 6 Spheres in Cylinder",
        points=points + points_c,
        lines=lines,
        circles=circles,
        raw_yaml={"ellipses": ellipses}
    )
    
    config = RenderConfig(figsize=(4, 12), line_width=2.0, show_points=False, show_labels=False)
    renderer = FigureRenderer(config)
    renderer.render(figure)
    renderer.save_png(str(OUTPUT_DIR / "spheres_in_cylinder.png"))
    renderer.close()

def create_raised_hemisphere():
    """
    Q6: Raised hemisphere in cylinder.
    """
    print("Generating 3D Raised Hemisphere diagram...")
    r = 3.0
    h = 6.0
    
    ellipses = [
        {"center": "T", "width": 2*r, "height": 0.6*r, "fill": True, "zorder": 4} # Top cap
    ]
    
    points = [
        Point("T", 0, h),
        Point("B_L", -r, 0), Point("B_R", r, 0),
        Point("T_L", -r, h), Point("T_R", r, h),
        Point("C", 0, 0)
    ]
    
    lines = [
        Line("B_L", "T_L"), Line("B_R", "T_R")
    ]
    
    arcs = [
        Arc(circle_center="C", start_point="B_R", end_point="B_L")
    ]
    
    # Base ellipse half-visible
    ellipses.append({"center": "C", "width": 2*r, "height": 0.6*r, "zorder": 1})
    
    figure = GeometryFigure(
        figure_type=FigureType.MENSURATION_COMBINED,
        description="3D Raised Hemisphere",
        points=points,
        lines=lines,
        arcs=arcs,
        raw_yaml={"ellipses": ellipses}
    )
    
    config = RenderConfig(figsize=(8, 8), line_width=2.5, show_points=False, show_labels=False)
    renderer = FigureRenderer(config)
    renderer.render(figure)
    renderer.save_png(str(OUTPUT_DIR / "raised_hemisphere.png"))
    renderer.close()

if __name__ == "__main__":
    create_iron_pole()
    create_sphere_in_cylinder()
    create_six_spheres()
    create_raised_hemisphere()
    print("Success: Generated solid 3D diagrams.")
