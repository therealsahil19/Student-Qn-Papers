"""
Batch Image Extraction for Class 8 Chapters
Extracts page images from chapter PDFs to organized folders.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pdf_processor import PDFProcessor

# Configuration
BASE_DIR = Path(__file__).parent.parent
PDF_DIR = BASE_DIR / "Aqsa Class 8 papers"
OUTPUT_DIR = Path(__file__).parent / "images_class_8"

# Chapter names mapping (based on R.D. Sharma Class 8)
CHAPTER_NAMES = {
    1: "Rational_Numbers",
    2: "Powers",
    3: "Squares_and_Square_Roots",
    4: "Cubes_and_Cube_Roots",
    5: "Playing_with_Numbers",
    # 6, 7, 8 already done - skip
    9: "Linear_Equations",
    10: "Direct_and_Inverse_Variations",
    11: "Time_and_Work",
    12: "Percentage",
    13: "Profit_Loss_Discount_Tax",
    14: "Compound_Interest",
    15: "Understanding_Quadrilaterals",
    16: "Parallelograms",
    17: "Construction_of_Quadrilaterals",
    18: "Visualising_3D_Shapes",
    19: "Surface_Area_and_Volume",
    20: "Data_Handling_I",
    21: "Data_Handling_II",
    22: "Mensuration_I",
    23: "Mensuration_II",
    24: "Introduction_to_Graphs",
    25: "Linear_Graphs",
    26: "Probability",
    27: "Exponents",
}

# Chapters to skip (already extracted)
SKIP_CHAPTERS = {6, 7, 8}


def extract_chapter(chapter_num: int, chapter_name: str, processor: PDFProcessor) -> bool:
    """Extract images from a single chapter PDF."""
    pdf_path = PDF_DIR / f"Mathematics Class VIII Chap{chapter_num}.pdf"
    output_path = OUTPUT_DIR / chapter_name
    
    if not pdf_path.exists():
        print(f"  [SKIP] PDF not found: {pdf_path.name}")
        return False
    
    if output_path.exists() and any(output_path.iterdir()):
        print(f"  [SKIP] Already extracted: {chapter_name}")
        return True
    
    print(f"  Extracting to {chapter_name}/...")
    try:
        pages = processor.convert_pdf_to_images(str(pdf_path), str(output_path))
        print(f"  [DONE] Extracted {len(pages)} pages")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    print("=" * 60)
    print("Class 8 Chapter Image Extraction")
    print("=" * 60)
    print(f"\nSource: {PDF_DIR}")
    print(f"Output: {OUTPUT_DIR}\n")
    
    # Initialize processor
    processor = PDFProcessor(dpi=200, output_format="png")
    backend_info = processor.get_backend_info()
    
    if not backend_info["available"]:
        print("ERROR: No PDF processing backend available!")
        print(backend_info["install_instructions"])
        return 1
    
    print(f"Using backend: {backend_info['backend']}\n")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each chapter
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for chapter_num in range(1, 28):
        if chapter_num in SKIP_CHAPTERS:
            print(f"Chapter {chapter_num}: [SKIP] Already done (6, 7, 8)")
            skip_count += 1
            continue
        
        chapter_name = CHAPTER_NAMES.get(chapter_num, f"Chapter_{chapter_num}")
        print(f"Chapter {chapter_num}: {chapter_name}")
        
        if extract_chapter(chapter_num, chapter_name, processor):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successfully extracted: {success_count}")
    print(f"Skipped (already done): {skip_count}")
    print(f"Failed: {fail_count}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
