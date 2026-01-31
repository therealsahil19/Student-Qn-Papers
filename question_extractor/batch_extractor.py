import os
import json
from pathlib import Path
from extractor import QuestionExtractor

def batch_extract(years, output_file):
    extractor = QuestionExtractor(profile="class_10")
    base_images_dir = Path(r"c:\Users\mehna\OneDrive\Desktop\Student Qn papers\question_extractor\images_class_10")
    
    # Enable target topics explicitly just in case
    target_topics = ["Similarity", "Loci", "Trigonometry"]
    
    print(f"Starting batch extraction for years: {years}")
    
    for year in years:
        year_dir = base_images_dir / str(year)
        if not year_dir.exists():
            print(f"Warning: Directory for {year} not found at {year_dir}")
            continue
            
        print(f"\n--- Processing {year} ---")
        image_paths = extractor.get_all_image_paths(str(year_dir))
        
        for idx, img_path in enumerate(image_paths, 1):
            print(f"  Processing page {idx}/{len(image_paths)}...")
            # Here we would normally call an AI model. 
            # Since I am the AI, I will generate the prompt and then the next step will involve me "extracting"
            # However, for this script to work autonomously if I were running it, it would need an API call.
            # In this context, I will use this script to structure my own work.
    
    # This script is a template for the workflow.
    # I will perform the extraction page-by-page as requested.

if __name__ == "__main__":
    # Example usage
    # batch_extract([2016, 2017, 2018, 2019, 2020], "geometry_trigo_batch1.json")
    pass
