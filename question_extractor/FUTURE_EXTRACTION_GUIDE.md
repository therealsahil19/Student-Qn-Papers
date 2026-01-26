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

---

## 📐 Geometry Question Extraction

Geometry questions require special handling for **figures/diagrams**. Use the `[FIGURE]` block format to capture geometric information.

### Figure Block Format

```
Q5 [4 marks] (medium)

    In the given figure, O is the center of the circle. PT is a tangent at T.
    If ∠TAB = 32°, find: (i) ∠TPA (ii) ∠TBA
    
    [FIGURE]
    type: circle_tangent
    description: |
        Circle with center O. Points A, T, B on the circle.
        PT is tangent at T, with P external to circle.
        Angle TAB = 32° (marked).
    elements:
      - circle: {center: O, points: [A, T, B]}
      - tangent: {circle: O, point: T, external_point: P}
    given_values:
      TAB: "32°"
    find_values: [TPA, TBA]
    [/FIGURE]
    
    Subtopic: Alternate Segment Theorem
    [Source: ICSE 2024]
```

### Supported Figure Types

| Type | Description |
|------|-------------|
| `bpt_triangle` | Basic Proportionality Theorem triangles |
| `similar_triangles` | Similarity proofs and calculations |
| `circle_tangent` | Tangent from external point, tangent properties |
| `circle_chord` | Intersecting chords, chord properties |
| `cyclic_quadrilateral` | Cyclic quads with angle properties |
| `alternate_segment` | Alternate segment theorem |
| `construction_locus` | Locus constructions |
| `construction_tangent` | Tangent construction from external point |
| `construction_circumcircle` | Circumcircle construction |
| `construction_incircle` | Incircle construction |

### Minimal Format (Description Only)

For simpler extraction, you can use just a description:

```
[FIGURE]
type: circle_theorem
description: |
    Circle with center O. Triangle ABC inscribed in circle.
    Angle BAC = 50° marked. Find angle BOC.
[/FIGURE]
```

See `Geometry_Questions_Template.txt` for complete examples of all figure types.

---

## 📄 Paper Generation

Generate formatted exam papers (PDF/Word) from your question banks.

### Basic Usage

```powershell
# Generate PDF from question bank
python paper_generator.py --input Geometry_Questions.txt --output exam.pdf

# Generate with specific topics
python paper_generator.py --input Geometry_Questions.txt --topics "Circles,Similarity" --output geo_paper.pdf

# Generate Word document
python paper_generator.py --input Geometry_Questions.txt --output exam.docx --format docx
```

### Required Dependencies

```powershell
pip install matplotlib reportlab python-docx PyYAML
```

### Features
- Automatic section distribution (MCQs in Section A, long answers in Section B)
- Figure rendering from `[FIGURE]` blocks
- ICSE exam format with instructions
- Customizable title, marks, and topics

---

## 📁 New Files Reference

| File | Purpose |
|------|---------|
| `geometry_schema.py` | Figure type definitions and [FIGURE] block parser |
| `figure_renderer.py` | Matplotlib-based geometry figure rendering |
| `paper_generator.py` | PDF/Word exam paper generation |
| `Geometry_Questions_Template.txt` | Template with geometry figure examples |

---

## 🧪 Testing Figure Rendering

Test the figure rendering system:

```powershell
# Test geometry schema parsing
python geometry_schema.py

# Test figure rendering (creates test_figures/ folder)
python figure_renderer.py --test

# Check paper generator dependencies
python paper_generator.py --check-deps
```

