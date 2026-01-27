# ICSE Class 10 Math Question Extractor

A comprehensive tool for extracting mathematics questions from PDF exam papers, managing a question bank, and generating new formatted exam papers with automatic geometry figure rendering.

## 🚀 Project Overview

This tool is designed to automate the lifecycle of creating math question banks:
1.  **Ingest**: Convert PDF exam papers into high-quality images.
2.  **Extract**: Identify and extract questions based on specific syllabus topics.
3.  **Organize**: Manage a structured text-based question bank.
4.  **Generate**: Create professional PDF/Word exam papers with diagrams.

---

## 📖 User Guide

### 1. Installation

Ensure you have Python installed. Install the required dependencies:

```bash
pip install PyMuPDF reportlab python-docx matplotlib PyYAML
```

### 2. Workflow

The standard workflow for processing papers is as follows:

#### Step 1: Batch Process PDFs
Take a batch of 4-5 PDF papers and convert them to images for analysis.

```bash
cd question_extractor
python extractor.py --pdf "../ICSE 2024.pdf" --prepare-images ./images
```

*Tip: You can use the `--batch-manifest` option to generate a tracking file for processing multiple pages.*

#### Step 2: Extract Questions
Run the extractor to analyze the images and generate text questions. The tool uses a topic configuration to identify relevant questions (e.g., Algebra, Geometry).

```bash
# Generate an AI prompt to help extract questions from the images
python extractor.py --generate-prompt
```

*Note: Use the generated prompt with an AI vision model (like Claude/GPT-4) to get the text, then save it to your `.txt` question bank (e.g., `Geometry_Questions.txt`).*

#### Step 3: Separation & Refinement
Once questions are in the text file:
1.  **Review**: Go through the text file.
2.  **Separate**: Identify which questions are purely text-based and which require geometric figures.
3.  **Gap Creation**: For geometry questions, ensure you have the `[FIGURE]` block structure ready or placeholders inserted.

#### Step 4: Draft Generation (Leaving Gaps)
Generate a draft of the exam paper. Use the `--no-figures` flag to leave placeholders/gaps where geometry figures will go. This allows you to verify the layout and text first.

```bash
python paper_generator.py --input Geometry_Questions.txt --output draft_paper.pdf --no-figures
```

#### Step 5: Geometric Figure Design
Fill in the `[FIGURE]` blocks in your text file using the supported schema.

Example `[FIGURE]` block:
```text
[FIGURE]
type: circle_tangent
description: Circle with center O, tangent PT.
elements:
  - circle: {center: O, points: [A, T, B]}
  - tangent: {circle: O, point: T, external_point: P}
given_values:
  TAB: "32°"
find_values: [TPA, TBA]
[/FIGURE]
```

#### Step 6: Final Paper Generation
Generate the final paper with all figures rendered.

```bash
python paper_generator.py --input Geometry_Questions.txt --output final_exam.pdf
```

---

## 💻 Developer Guide

### Architecture

The project is modularized into three core components residing in `question_extractor/`:

1.  **Extraction Engine** (`extractor.py`)
    *   Manages the topic syllabus (`topics_config.json`).
    *   Generates prompts for AI extraction.
    *   Parses extraction results into structured objects.

2.  **PDF Processor** (`pdf_processor.py`)
    *   Handles PDF-to-Image conversion.
    *   **Parallel Processing**: Uses `ProcessPoolExecutor` for high-performance batch processing.
    *   **Backends**: Supports `PyMuPDF` (default) and `pdf2image` as a fallback.

3.  **Generation Engine** (`paper_generator.py` & `figure_renderer.py`)
    *   **Paper Generator**: Parses the text question bank and uses `reportlab` (PDF) or `python-docx` (Word) to layout the paper.
    *   **Figure Renderer**: Reads `[FIGURE]` blocks, parses them via `geometry_schema.py`, and draws them using `matplotlib`.

### Key Modules & Customization

#### Adding New Topics
Edit `question_extractor/topics_config.json`. You can define new units, topics, keywords, and formulas.

#### Customizing Figure Types
*   **Schema**: Defined in `geometry_schema.py`. Add new data classes for new shapes.
*   **Rendering**: Update `figure_renderer.py` to handle the drawing logic for new shapes.

#### PDF Backend
The `PDFProcessor` class automatically detects available libraries.
*   `_convert_with_pymupdf`: Fast, robust, no external deps (besides wheels).
*   `_convert_with_pdf2image`: Requires Poppler installed on the system.

### Command Reference

| Task | Command |
|------|---------|
| **List Topics** | `python extractor.py --list-topics` |
| **Check Deps** | `python extractor.py --check` |
| **Make Images** | `python extractor.py --pdf "paper.pdf" --prepare-images ./imgs` |
| **Draft PDF** | `python paper_generator.py -i bank.txt -o draft.pdf --no-figures` |
| **Final PDF** | `python paper_generator.py -i bank.txt -o final.pdf` |
