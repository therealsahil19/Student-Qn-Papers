# 📖 Future Extraction Guide

This guide explains how to continue extracting questions across all ICSE Class 10 Mathematics topics (Commercial Math, Algebra, Geometry, etc.) when you add more PDF papers to the project.

## Directory Overview

- `/` : Root directory containing PDF papers.
- `/question_extractor/` : Core workspace for extraction.
    - `/images/` : Subdirectories for each paper containing page images.
    - `extractor.py` : Tool for PDF conversion and prompt generation.
    - `update_summary.py` : Utility to recount and update the summary headers/tables.
    - `Commercial_Math_Questions.txt` : Question bank for GST, Banking, Shares.
    - `Algebra_Questions.txt` : Question bank for Inequations, Quadratics, Factorisation.
    - `AP_GP_Matrices_Probability_Questions.txt` : Combined question bank for specific Algebra units.

---

## 🚀 Step-by-Step Workflow

### 1. Prepare New PDFs
1. Place your new PDF files in the root folder.
2. Open a terminal in the `question_extractor` directory.
3. Run the following command to convert the PDF to images for analysis:
   ```powershell
   python extractor.py --pdf "../Path/To/Your/NewPaper.pdf" --prepare-images "./images/PaperName_Folder"
   ```

### 2. Identify Target Topics
Determine which questions you want to extract. You can enable specific topics in `topics_config.json` or use the command line:
```powershell
# List all topics to see their status
python extractor.py --list-topics
```

### 3. Visual Analysis & AI Extraction
1. Open the folder you created in `./images/PaperName_Folder`.
2. Use an AI assistant to help extract questions. Generate a tailored prompt:
   ```powershell
   python extractor.py --generate-prompt
   ```
3. Paste this prompt and the images into your AI tool.

### 4. Append Questions to Bank
1. Copy the JSON/Text output from the AI.
2. Open the relevant question bank file (e.g., `Algebra_Questions.txt`).
3. Append the new questions to the end of the appropriate topic sections.
4. **Tip**: Ensure you follow the file format exactly:
   ```
   Q[Num] [[Marks]] (Difficulty) 
   
       [Exact Question Text]
       Subtopic: [Specific Type]
       [Source: Name Of Paper]
       
       ----------------------------------------
   ```

### 5. Update Summaries
Instead of manually updating the "Number of Questions" headers and the bottom Summary table, run the helper script:
```powershell
# Update specific files
python update_summary.py "Algebra_Questions.txt" "AP_GP_Matrices_Probability_Questions.txt"

# Or update all known files
python update_summary.py *.txt
```
This script will:
- Scan the entire file for "Topic: ..." headers and question markers.
- Correct the question counts for each category.
- Update the "Total questions" and "Last Updated" timestamps.
- Refresh the SUMMARY/CUMULATIVE SUMMARY table at the bottom.

---

## 🛠️ Troubleshooting

- **PDF conversion fails?** Ensure `PyMuPDF` is installed (`pip install PyMuPDF`).
- **Summary script errors?** Keep the headers formatted as `Topic: [Name]` and the question markers as `Q[Num]`. Do not delete the `SUMMARY` or `CUMULATIVE SUMMARY` markers at the bottom.
- **Wrong counts?** The script counts lines starting with `Q` followed by a digit or letter. Ensure your question numbers follow this pattern.
