"""
Geometry Figure Renderer Module

Renders GeometryFigure objects to PNG/SVG images using matplotlib.
Supports various geometry figure types common in ICSE Class 10 Mathematics.

Usage:
    from geometry_schema import FigureParser
    from figure_renderer import FigureRenderer
    
    parser = FigureParser()
    figure = parser.parse(figure_block)
    
    renderer = FigureRenderer()
    renderer.render(figure)
    renderer.save_png("output.png")
"""

import math
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Arc, Circle as MplCircle, FancyArrowPatch
    from matplotlib.lines import Line2D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Figure rendering will be disabled.")

# Import our schema
try:
    from geometry_schema import (
        GeometryFigure, FigureType, Point, Line, Circle, 
        Angle, Triangle, Quadrilateral, Tangent, Arc as GeoArc
    )
except ImportError:
    # For standalone testing
    pass


@dataclass
class RenderConfig:
    """Configuration for figure rendering."""
    
    # Canvas settings
    figsize: Tuple[float, float] = (8, 8)
    dpi: int = 150
    background_color: str = 'white'
    
    # Default geometry settings
    default_radius: float = 3.0
    point_size: float = 50
    
    # Colors
    line_color: str = '#2c3e50'
    circle_color: str = '#3498db'
    angle_arc_color: str = '#e74c3c'
    construction_color: str = '#95a5a6'
    fill_color: str = '#ecf0f1'
    
    # Line styles
    line_width: float = 1.5
    construction_line_width: float = 1.0
    
    # Font settings
    font_size: int = 12
    font_family: str = 'serif'
    label_offset: float = 0.3
    
    # Angle arc settings
    angle_arc_radius: float = 0.5
    
    # Margins
    margin: float = 1.5


class PointLayoutEngine:
    """
    Calculates appropriate positions for points based on figure structure.
    
    Uses geometric rules to position points when coordinates are not specified.
    """
    
    def __init__(self, config: RenderConfig):
        self.config = config
        self.positions: Dict[str, Tuple[float, float]] = {}
    
    def calculate_positions(self, figure: GeometryFigure) -> Dict[str, Tuple[float, float]]:
        """Calculate positions for all points in the figure."""
        
        self.positions = {}
        
        # First, use any explicitly defined positions
        for point in figure.points:
            if point.x is not None and point.y is not None:
                self.positions[point.label] = (point.x, point.y)
        
        # Position circle centers
        for i, circle in enumerate(figure.circles):
            if circle.center not in self.positions:
                # Default center at origin or offset for multiple circles
                self.positions[circle.center] = (i * 5, 0)
        
        # Position points on circles
        for circle in figure.circles:
            self._position_points_on_circle(circle, figure)
        
        # Position triangle vertices
        for triangle in figure.triangles:
            self._position_triangle_vertices(triangle, figure)
        
        # Position quadrilateral vertices
        for quad in figure.quadrilaterals:
            self._position_quad_vertices(quad, figure)
        
        # Position tangent points
        for tangent in figure.tangents:
            self._position_tangent_points(tangent, figure)
        
        # Position remaining points
        self._position_remaining_points(figure)
        
        return self.positions
    
    def _position_points_on_circle(self, circle: Circle, figure: GeometryFigure):
        """Position points that lie on a circle."""
        
        center = self.positions.get(circle.center, (0, 0))
        radius = circle.radius if circle.radius else self.config.default_radius
        
        # Position explicitly listed points on circle
        points_to_position = [p for p in circle.points_on_circle if p not in self.positions]
        
        if not points_to_position:
            return
        
        # Distribute points evenly, but with aesthetically pleasing angles
        n = len(points_to_position)
        start_angle = 90  # Start from top
        
        for i, point_label in enumerate(points_to_position):
            # Use golden angle for better distribution
            angle = start_angle - (i * 360 / n)
            rad = math.radians(angle)
            x = center[0] + radius * math.cos(rad)
            y = center[1] + radius * math.sin(rad)
            self.positions[point_label] = (x, y)
    
    def _position_triangle_vertices(self, triangle: Triangle, figure: GeometryFigure):
        """Position triangle vertices."""
        
        # Check if inscribed in a circle
        if triangle.inscribed_in and triangle.inscribed_in in self.positions:
            center = self.positions[triangle.inscribed_in]
            # Find the circle
            circle = next((c for c in figure.circles if c.center == triangle.inscribed_in), None)
            radius = circle.radius if circle and circle.radius else self.config.default_radius
            
            # Position vertices on circle at nice angles
            angles = [90, 210, 330]  # Equilateral-ish positions
            for i, vertex in enumerate(triangle.vertices):
                if vertex not in self.positions:
                    rad = math.radians(angles[i])
                    x = center[0] + radius * math.cos(rad)
                    y = center[1] + radius * math.sin(rad)
                    self.positions[vertex] = (x, y)
        else:
            # Standalone triangle
            vertices = triangle.vertices
            # Place as isoceles triangle
            default_positions = [(0, 3), (-2.5, -1.5), (2.5, -1.5)]
            for i, vertex in enumerate(vertices):
                if vertex not in self.positions:
                    self.positions[vertex] = default_positions[i]
    
    def _position_quad_vertices(self, quad: Quadrilateral, figure: GeometryFigure):
        """Position quadrilateral vertices."""
        
        if quad.is_cyclic and quad.inscribed_in and quad.inscribed_in in self.positions:
            center = self.positions[quad.inscribed_in]
            circle = next((c for c in figure.circles if c.center == quad.inscribed_in), None)
            radius = circle.radius if circle and circle.radius else self.config.default_radius
            
            # Position on circle
            angles = [120, 60, -30, -120]
            for i, vertex in enumerate(quad.vertices):
                if vertex not in self.positions:
                    rad = math.radians(angles[i])
                    x = center[0] + radius * math.cos(rad)
                    y = center[1] + radius * math.sin(rad)
                    self.positions[vertex] = (x, y)
        else:
            # General quadrilateral
            default_positions = [(-2, 2), (2, 2), (3, -2), (-3, -2)]
            for i, vertex in enumerate(quad.vertices):
                if vertex not in self.positions:
                    self.positions[vertex] = default_positions[i]
    
    def _position_tangent_points(self, tangent: Tangent, figure: GeometryFigure):
        """Position tangent-related points."""
        
        if tangent.circle_center in self.positions:
            center = self.positions[tangent.circle_center]
            circle = next((c for c in figure.circles if c.center == tangent.circle_center), None)
            radius = circle.radius if circle and circle.radius else self.config.default_radius
            
            # Position point of tangency
            if tangent.point_of_tangency not in self.positions:
                # Default: right side of circle
                self.positions[tangent.point_of_tangency] = (center[0] + radius, center[1])
            
            # Position external point
            if tangent.external_point and tangent.external_point not in self.positions:
                # Place external point further out along tangent direction
                tan_point = self.positions[tangent.point_of_tangency]
                direction = (tan_point[0] - center[0], tan_point[1] - center[1])
                # Perpendicular direction for tangent line
                perp = (-direction[1], direction[0])
                length = math.sqrt(perp[0]**2 + perp[1]**2)
                if length > 0:
                    perp = (perp[0]/length * 2, perp[1]/length * 2)
                self.positions[tangent.external_point] = (
                    tan_point[0] + perp[0],
                    tan_point[1] + perp[1]
                )
    
    def _position_remaining_points(self, figure: GeometryFigure):
        """Position any remaining undefined points."""
        
        all_labels = figure.get_all_point_labels()
        undefined = [label for label in all_labels if label not in self.positions]
        
        # Place remaining points in a grid pattern
        for i, label in enumerate(undefined):
            row = i // 3
            col = i % 3
            self.positions[label] = (-4 + col * 2, 4 - row * 2)


class FigureRenderer:
    """
    Renders GeometryFigure objects to images.
    
    Uses matplotlib to draw geometric elements with proper styling.
    """
    
    def __init__(self, config: Optional[RenderConfig] = None):
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for figure rendering. Install with: pip install matplotlib")
        
        self.config = config or RenderConfig()
        self.layout_engine = PointLayoutEngine(self.config)
        self.fig = None
        self.ax = None
        self.positions = {}
    
    def render(self, figure: GeometryFigure) -> 'FigureRenderer':
        """
        Render a geometry figure.
        
        Returns self for method chaining.
        """
        # Calculate point positions
        self.positions = self.layout_engine.calculate_positions(figure)
        
        # Create figure and axes
        self.fig, self.ax = plt.subplots(1, 1, figsize=self.config.figsize)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor(self.config.background_color)
        
        # Render elements in order (back to front)
        self._render_circles(figure)
        self._render_lines(figure)
        self._render_triangles(figure)
        self._render_quadrilaterals(figure)
        self._render_tangents(figure)
        self._render_angles(figure)
        self._render_points(figure)
        self._render_labels()
        
        # Set axis limits with margin
        self._set_axis_limits()
        
        # Hide axes
        self.ax.axis('off')
        
        return self
    
    def _render_circles(self, figure: GeometryFigure):
        """Render circles."""
        for circle in figure.circles:
            if circle.center in self.positions:
                center = self.positions[circle.center]
                radius = circle.radius if circle.radius else self.config.default_radius
                
                # Draw circle
                circle_patch = MplCircle(
                    center, radius,
                    fill=False,
                    edgecolor=self.config.circle_color,
                    linewidth=self.config.line_width
                )
                self.ax.add_patch(circle_patch)
    
    def _render_lines(self, figure: GeometryFigure):
        """Render line segments."""
        for line in figure.lines:
            if line.start in self.positions and line.end in self.positions:
                start = self.positions[line.start]
                end = self.positions[line.end]
                
                # Determine line style
                linestyle = {
                    'solid': '-',
                    'dashed': '--',
                    'dotted': ':'
                }.get(line.style, '-')
                
                self.ax.plot(
                    [start[0], end[0]], [start[1], end[1]],
                    color=self.config.line_color,
                    linewidth=self.config.line_width,
                    linestyle=linestyle,
                    zorder=2
                )
    
    def _render_triangles(self, figure: GeometryFigure):
        """Render triangles."""
        for triangle in figure.triangles:
            vertices = triangle.vertices
            if all(v in self.positions for v in vertices):
                coords = [self.positions[v] for v in vertices]
                coords.append(coords[0])  # Close the triangle
                
                xs, ys = zip(*coords)
                
                linestyle = '--' if triangle.style == 'dashed' else '-'
                
                self.ax.plot(
                    xs, ys,
                    color=self.config.line_color,
                    linewidth=self.config.line_width,
                    linestyle=linestyle,
                    zorder=2
                )
    
    def _render_quadrilaterals(self, figure: GeometryFigure):
        """Render quadrilaterals."""
        for quad in figure.quadrilaterals:
            vertices = quad.vertices
            if all(v in self.positions for v in vertices):
                coords = [self.positions[v] for v in vertices]
                coords.append(coords[0])  # Close the shape
                
                xs, ys = zip(*coords)
                
                self.ax.plot(
                    xs, ys,
                    color=self.config.line_color,
                    linewidth=self.config.line_width,
                    zorder=2
                )
    
    def _render_tangents(self, figure: GeometryFigure):
        """Render tangent lines."""
        for tangent in figure.tangents:
            # Draw line from tangent point to external point
            if tangent.point_of_tangency in self.positions:
                tan_point = self.positions[tangent.point_of_tangency]
                
                if tangent.external_point and tangent.external_point in self.positions:
                    ext_point = self.positions[tangent.external_point]
                    
                    self.ax.plot(
                        [tan_point[0], ext_point[0]], [tan_point[1], ext_point[1]],
                        color=self.config.line_color,
                        linewidth=self.config.line_width,
                        zorder=2
                    )
                
                # Draw small perpendicular mark at tangent point
                if tangent.circle_center in self.positions:
                    center = self.positions[tangent.circle_center]
                    self._draw_perpendicular_mark(center, tan_point)
    
    def _draw_perpendicular_mark(self, center: Tuple[float, float], tan_point: Tuple[float, float]):
        """Draw a small square to indicate perpendicularity at tangent point."""
        
        # Direction from center to tangent point
        dx = tan_point[0] - center[0]
        dy = tan_point[1] - center[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return
        
        # Normalize
        dx, dy = dx/length, dy/length
        
        # Perpendicular direction
        px, py = -dy, dx
        
        # Size of the perpendicular mark
        size = 0.2
        
        # Four corners of the small square
        p1 = (tan_point[0], tan_point[1])
        p2 = (tan_point[0] + px * size, tan_point[1] + py * size)
        p3 = (tan_point[0] + px * size - dx * size, tan_point[1] + py * size - dy * size)
        p4 = (tan_point[0] - dx * size, tan_point[1] - dy * size)
        
        # Draw the square
        xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
        ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
        
        self.ax.plot(xs, ys, color=self.config.line_color, linewidth=0.8, zorder=3)
    
    def _render_angles(self, figure: GeometryFigure):
        """Render angle arcs and labels."""
        for angle in figure.angles:
            if all(p in self.positions for p in [angle.vertex, angle.ray1_end, angle.ray2_end]):
                vertex = self.positions[angle.vertex]
                p1 = self.positions[angle.ray1_end]
                p2 = self.positions[angle.ray2_end]
                
                # Calculate angles
                angle1 = math.degrees(math.atan2(p1[1] - vertex[1], p1[0] - vertex[0]))
                angle2 = math.degrees(math.atan2(p2[1] - vertex[1], p2[0] - vertex[0]))
                
                # Draw arc
                if angle.marked:
                    arc = Arc(
                        vertex,
                        self.config.angle_arc_radius * 2,
                        self.config.angle_arc_radius * 2,
                        angle=0,
                        theta1=min(angle1, angle2),
                        theta2=max(angle1, angle2),
                        color=self.config.angle_arc_color,
                        linewidth=1.0,
                        zorder=4
                    )
                    self.ax.add_patch(arc)
                
                # Add angle value label
                if angle.value:
                    mid_angle = (angle1 + angle2) / 2
                    label_radius = self.config.angle_arc_radius * 1.5
                    label_x = vertex[0] + label_radius * math.cos(math.radians(mid_angle))
                    label_y = vertex[1] + label_radius * math.sin(math.radians(mid_angle))
                    
                    self.ax.annotate(
                        angle.value,
                        (label_x, label_y),
                        fontsize=self.config.font_size - 2,
                        ha='center', va='center',
                        color=self.config.angle_arc_color,
                        zorder=5
                    )
    
    def _render_points(self, figure: GeometryFigure):
        """Render point markers."""
        for label, pos in self.positions.items():
            self.ax.scatter(
                pos[0], pos[1],
                s=self.config.point_size,
                c=self.config.line_color,
                zorder=10
            )
    
    def _render_labels(self):
        """Render point labels."""
        for label, pos in self.positions.items():
            # Determine label position offset based on position relative to center
            center_x = sum(p[0] for p in self.positions.values()) / len(self.positions)
            center_y = sum(p[1] for p in self.positions.values()) / len(self.positions)
            
            dx = pos[0] - center_x
            dy = pos[1] - center_y
            length = math.sqrt(dx**2 + dy**2)
            
            if length > 0:
                offset_x = (dx / length) * self.config.label_offset
                offset_y = (dy / length) * self.config.label_offset
            else:
                offset_x, offset_y = self.config.label_offset, self.config.label_offset
            
            self.ax.annotate(
                label,
                (pos[0] + offset_x, pos[1] + offset_y),
                fontsize=self.config.font_size,
                fontfamily=self.config.font_family,
                ha='center', va='center',
                zorder=11
            )
    
    def _set_axis_limits(self):
        """Set appropriate axis limits based on rendered content."""
        if not self.positions:
            return
        
        xs = [p[0] for p in self.positions.values()]
        ys = [p[1] for p in self.positions.values()]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        margin = self.config.margin
        
        # Make it square
        x_range = x_max - x_min
        y_range = y_max - y_min
        max_range = max(x_range, y_range)
        
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        self.ax.set_xlim(x_center - max_range/2 - margin, x_center + max_range/2 + margin)
        self.ax.set_ylim(y_center - max_range/2 - margin, y_center + max_range/2 + margin)
    
    def save_png(self, output_path: str, dpi: Optional[int] = None):
        """Save the rendered figure as PNG."""
        if self.fig is None:
            raise ValueError("No figure rendered. Call render() first.")
        
        self.fig.savefig(
            output_path,
            dpi=dpi or self.config.dpi,
            bbox_inches='tight',
            facecolor=self.config.background_color,
            edgecolor='none'
        )
        print(f"Saved PNG: {output_path}")
    
    def save_svg(self, output_path: str):
        """Save the rendered figure as SVG."""
        if self.fig is None:
            raise ValueError("No figure rendered. Call render() first.")
        
        self.fig.savefig(
            output_path,
            format='svg',
            bbox_inches='tight',
            facecolor=self.config.background_color,
            edgecolor='none'
        )
        print(f"Saved SVG: {output_path}")
    
    def show(self):
        """Display the figure interactively."""
        if self.fig is None:
            raise ValueError("No figure rendered. Call render() first.")
        plt.show()
    
    def close(self):
        """Close the figure and free memory."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None


def render_figure_from_text(figure_block: str, output_path: str) -> str:
    """
    Convenience function to render a figure block directly to an image.
    
    Args:
        figure_block: Text content of [FIGURE]...[/FIGURE] block
        output_path: Path to save the image
        
    Returns:
        Path to the saved image
    """
    from geometry_schema import FigureParser
    
    parser = FigureParser()
    figure = parser.parse(figure_block)
    
    renderer = FigureRenderer()
    renderer.render(figure)
    
    if output_path.endswith('.svg'):
        renderer.save_svg(output_path)
    else:
        renderer.save_png(output_path)
    
    renderer.close()
    return output_path


# ============================================================================
# Testing
# ============================================================================

def test(output_dir: str = "./test_figures"):
    """Test figure rendering with sample figures."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot run tests: matplotlib not installed")
        return
    
    from geometry_schema import FigureParser, FIGURE_TEMPLATES
    
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
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./test_figures"
        test(output_dir)
    else:
        print("Usage: python figure_renderer.py --test [output_directory]")
        print("\nThis module provides:")
        print("  - FigureRenderer: Renders GeometryFigure objects to PNG/SVG")
        print("  - render_figure_from_text(): Direct text-to-image conversion")
