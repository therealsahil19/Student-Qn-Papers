import os
import sys
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geometry_schema import FigureParser
from figure_renderer import FigureRenderer

def ensure_output_directory(path: str) -> Path:
    """Ensure the output directory exists and return it as a Path object."""
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def create_diagram(name: str, yaml_content: str, output_dir: Path, output_format: str = "svg", renderer: Optional[FigureRenderer] = None) -> str:
    """
    Create a diagram from YAML content.
    
    Args:
        name: Name of the diagram (used for filename)
        yaml_content: YAML description of the diagram
        output_dir: Directory to save the diagram
        output_format: Output format (svg or png)
        renderer: Optional existing renderer instance to reuse
        
    Returns:
        Path to the saved file
    """
    print(f"Generating {name}...")
    
    should_close_renderer = False
    if renderer is None:
        renderer = FigureRenderer()
        should_close_renderer = True
        
    try:
        parser = FigureParser()
        figure = parser.parse(yaml_content)
        renderer.render(figure)
        
        output_path = output_dir / f"{name}.{output_format}"
        
        if output_format.lower() == "svg":
            renderer.save_svg(str(output_path))
        else:
            renderer.save_png(str(output_path))
            
        print(f"Saved to {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error generating {name}: {e}")
        return ""
        
    finally:
        if should_close_renderer:
            renderer.close()
