# Student Question Papers & Exam Generator Framework

A robust, modular framework for managing mathematics question banks, extracting content from PDFs via AI, and generating professional exam papers. This system supports specialized workflows for **ICSE Class 10** and **Class 8**.

## 🚀 Features

*   **AI-Ready Extraction**: Convert PDF papers to images and generate optimized prompts for LLM-based question extraction.
*   **Question Bank Management**: Maintain topic-wise text files with automatic summary updating.
*   **Professional Paper Generation**: Create PDF or Word (DOCX) exam papers with proper formatting, headers, and instructions.
*   **Geometry Engine**: Render complex 2D and 3D geometric figures directly from text descriptions using a custom YAML schema.
*   **Batch Processing**: Tools for handling large sets of chapter PDFs (specifically for Class 8).

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher
*   [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (Required only if using `pdf2image` backend; `PyMuPDF` is the default and doesn't require this).

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 📚 Core Workflows

### 1. Automated Agent Workflow (Recommended)
This workflow is designed for AI Agents (Antigravity) to autonomously process PDF papers and extract questions without human intervention.

**See [AGENTS.md](AGENTS.md) for the detailed protocol.**

**Summary:**
1.  **Job Creation:** Agent runs `extractor.py` to prepare images and a "Job Manifest".
    ```bash
    python question_extractor/extractor.py --pdf "paper.pdf" --prepare-images "./img_job" --quiet
    python question_extractor/extractor.py --batch-manifest "./img_job" --source "2024" --quiet
    ```
2.  **Self-Execution:** Agent reads `extraction_manifest.json`, which contains both the list of images and the precise instruction prompt.
3.  **Extraction:** Agent loops through the images, applying the prompt using its vision capabilities, and saves the results.

### 2. Manual Workflow (Legacy)
For users manually extracting questions using external tools.

**Step A: Extract Questions**
1.  **Prepare Images:** Convert a PDF exam paper into images.
    ```bash
    python question_extractor/extractor.py --pdf "Class 10pdfs/icse/2024.pdf" --prepare-images "./images/2024_paper"
    ```
2.  **Generate Prompt:** Create a context-aware prompt to copy-paste into an LLM.
    ```bash
    python question_extractor/extractor.py --generate-prompt --topics "GST,Banking"
    ```
3.  **Save Output:** Paste the AI's JSON/Text output into your question bank file.

**Step B: Maintain Bank**
Update the summary counts in your question bank file.
```bash
python question_extractor/update_summary.py "Commercial_Math_Questions.txt"
```

**Step C: Generate Exam Paper**
Create a formatted PDF paper from your question bank.
```bash
python question_extractor/paper_generator.py --input "Commercial_Math_Questions.txt" --output "Mock_Test.pdf" --total-marks 80
```

### 2. Class 8 (Specialized Workflow)
A batch-processing workflow for textbook chapters.

**Step A: Batch Image Extraction**
Extract images from all Class 8 chapter PDFs defined in the script.
```bash
python question_extractor/extract_class8_images.py
```

**Step B: Term Paper Generation**
Generate a specific format term paper (uses `create_class8_pdf.py`).
*Note: This script may require modification of input/output paths before running.*
```bash
python question_extractor/create_class8_pdf.py
```

---

## 🔧 Tool Reference

All scripts should be run from the root directory of the project.

### `question_extractor/extractor.py`
The main CLI tool for PDF processing and prompt generation.

| Flag | Description |
|------|-------------|
| `--list-topics` | Show all configured topics and their status. |
| `--pdf <path>` | Path to the source PDF file. |
| `--prepare-images <dir>` | Convert PDF pages to images in the specified folder. |
| `--generate-prompt` | Generate a prompt for LLM extraction based on enabled topics. |
| `--topics "T1,T2"` | Override config to extract specific topics (comma-separated). |
| `--profile <name>` | Switch syllabus profile (`class_10` or `class_8`). |

### `question_extractor/paper_generator.py`
Generates exam papers from text-based question banks.

| Flag | Description |
|------|-------------|
| `--input <files>` | One or more `.txt` question bank files. |
| `--output <file>` | Output filename (ends in `.pdf` or `.docx`). |
| `--format [pdf/docx]` | Force specific output format. |
| `--topics "T1,T2"` | Filter questions to include only specific topics. |
| `--total-marks <N>` | Set total marks (default: 80). |
| `--no-figures` | Disable geometry figure rendering. |

### `question_extractor/update_summary.py`
Updates the "Number of Questions" headers and the summary table in a question bank file.
```bash
python question_extractor/update_summary.py <path_to_file>
```

### `question_extractor/extract_class8_images.py`
**Specialized Tool**: Batch processes specific Class 8 chapter PDFs defined in the `CHAPTER_NAMES` dictionary within the script. useful for bulk conversion.

### `generate_exam_diagrams.py`
**Standalone Tool**: Generates high-quality 3D mensuration diagrams (e.g., spheres in cylinders) that are too complex for the standard schema.
```bash
python generate_exam_diagrams.py
```

### `identify_chapters.py`
**Utility**: Reads the first few lines of PDF files to help identify their content. Useful when files are unnamed.
*Note: Requires editing the file list inside the script.*

---

## 🎨 Geometry & Figure Engine

The project supports defining geometry figures directly in the question text using `[FIGURE]` blocks.

### Example Block
Embed this in your question text file:
```yaml
[FIGURE]
type: circle_tangent
description: Circle with center O, tangent PT from external point P.
elements:
  - circle: {center: O, radius: 3}
  - tangent: {circle: O, point: T, external_point: P}
  - line: {points: [O, P], style: dashed}
[/FIGURE]
```

### Supported Types
Defined in `question_extractor/geometry_schema.py`:
*   **Circles**: `circle_inscribed_angle`, `circle_tangent`, `cyclic_quadrilateral`, `alternate_segment`.
*   **Triangles**: `similar_triangles`, `bpt_triangle`.
*   **Constructions**: `construction_circumcircle`, `construction_incircle`.
*   **Mensuration**: `mensuration_cylinder`, `mensuration_cone`.

### Figure Renderer
The `figure_renderer.py` module uses `matplotlib` to render these schemas into PNG images which are then embedded into the generated PDF/DOCX.

---

## ⚙️ Configuration

Syllabus definitions are stored in `question_extractor/configs/`.
*   **`class_10.json`**: The master syllabus for ICSE 2026.
    - Defines Units (Commercial Math, Algebra, etc.).
    - Defines Topics within units (GST, Banking).
    - `keywords`: Used by `extractor.py` to prompt the AI on what to look for.
    - `formulas`: Included in prompts to help the AI identify question types.

- **`class_8.json`**: Simplified syllabus for Class 8.
    - Topics: Profit/Loss, Interest, Algebraic Identities, etc.
    - Used when running `extractor.py --profile class_8`.

---

## ⚠️ Troubleshooting

1.  **"PDF processing backend not available"**:
    *   Ensure `PyMuPDF` is installed (`pip install PyMuPDF`). It is the default and recommended backend.
    *   If using `pdf2image`, you must have [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) installed and added to your system PATH.

2.  **Import Errors**:
    *   Ensure you run scripts from the **root directory** (e.g., `python question_extractor/extractor.py`, NOT `cd question_extractor && python extractor.py`).
    *   The scripts rely on relative imports based on the project root.

3.  **"File not found" in `create_class8_pdf.py`**:
    *   This script contains hardcoded paths. Open the file and update the `output_path` and `text_file` variables to match your system.

