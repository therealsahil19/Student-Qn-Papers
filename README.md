# Student Question Papers & Exam Generator Framework

A robust, modular framework for managing mathematics question banks, extracting content from PDFs via AI, and generating professional exam papers. This system supports specialized workflows for **ICSE Class 10** and **Class 8**.

## 🚀 Features

*   **AI-Ready Extraction**: Convert PDF papers to images and generate optimized prompts for LLM-based question extraction.
*   **Question Bank Management**: Maintain topic-wise text files with automatic summary updating.
*   **Professional Paper Generation**: Create PDF or Word (DOCX) exam papers with proper formatting, headers, and instructions.
*   **Geometry Engine**: Render complex 2D and 3D geometric figures directly from text descriptions using a custom YAML schema.
*   **Batch Processing**: Tools for handling large sets of papers (hundreds of pages), including checkpointing, prioritization, and recursive directory scanning.
*   **Multi-Profile Support**: Switch between different syllabi (e.g., Class 10, Class 8) using profiles.
*   **Atomic Updates**: Safe appending of results to question banks without data loss.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher
*   **Recommended**: [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`fitz`) for faster, pure-Python PDF processing.
*   **Optional**: [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (Required only if using `pdf2image` backend).

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
1.  **Job Creation (Recursive):** Agent runs `extractor.py` to scan a root directory for all images and prepare a "Job Manifest".
    ```bash
    python question_extractor/extractor.py --batch-manifest "./images_root" --recursive --quiet
    ```
    *This creates `extraction_manifest.json` containing all pages found.*

2.  **Self-Execution:** Agent reads `extraction_manifest.json`, which contains both the list of images and the precise instruction prompt.
3.  **Extraction:** Agent loops through the images, applying the prompt using its vision capabilities, and saves the results.
4.  **Atomic Save:** Agent appends results safely using the append tool.
    ```bash
    python question_extractor/extractor.py --append-results "temp_results.json" --target "Questions.txt" --quiet
    ```

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

### 3. Class 8 Workflow
For extracting questions from Class 8 materials.

**Configuration**:
The system uses `question_extractor/configs/class_8.json` to define the syllabus (Algebra, Arithmetic, Mensuration, Statistics).

**Execution**:
Use the `--profile class_8` flag with the standard extractor tools.
```bash
python question_extractor/extractor.py --profile class_8 --generate-prompt
```

---

## 📦 Batch Processing & Checkpoints

For processing large volumes of papers (e.g., hundreds of pages), the system provides a checkpointing workflow to manage state and prioritize content.

### Workflow
1.  **Generate Master Manifest**:
    Run the extractor recursively on your image root.
    ```bash
    python question_extractor/extractor.py --batch-manifest "images_root" --recursive --quiet
    ```
    This creates `images_root/extraction_manifest.json`.

2.  **Create Checkpoint**:
    Sort and prioritize pages (Yearly Papers > SQP > Others) into a queue.
    ```bash
    python create_checkpoint.py
    ```
    This reads `extraction_manifest.json` (path hardcoded to `question_extractor/images_class_10/extraction_manifest.json`, adjust if needed) and creates `checkpoint_manifest.json`.

3.  **Pop Batch**:
    Retrieve the next N pages to process and remove them from the queue.
    ```bash
    python pop_batch.py 20
    ```
    This outputs a JSON array of 20 pages and updates `checkpoint_manifest.json`.

---

## 🔧 Tool Reference

All scripts should be run from the root directory of the project.

### `question_extractor/extractor.py`
The main CLI tool for PDF processing, prompt generation, and bank management.

| Flag | Description |
|------|-------------|
| `--list-topics` | Show all configured topics and their status. |
| `--list-units` | List all units in the syllabus. |
| `--check` | Check dependencies and configuration. |
| `--syllabus-info` | Show detailed syllabus information. |
| `--pdf <path>` | Path to the source PDF file. |
| `--prepare-images <dir>` | Convert PDF pages to images in the specified folder. |
| `--generate-prompt` | Generate a prompt for LLM extraction based on enabled topics. |
| `--topics "T1,T2"` | Override config to extract specific topics (comma-separated). |
| `--enable-topic <topic>` | Enable a specific topic in the configuration. |
| `--disable-topic <topic>` | Disable a specific topic in the configuration. |
| `--profile <name>` | Switch syllabus profile (`class_10` or `class_8`). |
| `--recursive` | Recursively search for images in subdirectories (used with `--batch-manifest`). |
| `--batch-manifest <dir>` | Generate batch extraction manifest for images directory. |
| `--source <name>` | Source paper name for batch extraction (used with `--batch-manifest`). |
| `--append-results <file>` | Append questions from JSON/Text file to a target bank using atomic writes. |
| `--target <file>` | Target file for appending results (used with `--append-results`). |
| `--quiet` | Suppress verbose output (useful for agent execution). |

### `question_extractor/paper_generator.py`
Generates exam papers from text-based question banks.

| Flag | Description |
|------|-------------|
| `--input <files>` | One or more `.txt` question bank files. |
| `--output <file>` | Output filename (ends in `.pdf` or `.docx`). |
| `--format [pdf/docx/word]` | Force specific output format (default: pdf). |
| `--title <text>` | Set the title of the exam paper. |
| `--subtitle <text>` | Set the subtitle of the exam paper. |
| `--topics "T1,T2"` | Filter questions to include only specific topics. |
| `--total-marks <N>` | Set total marks (default: 80). |
| `--check-deps` | Check available dependencies and exit. |
| `--no-figures` | Disable geometry figure rendering (placeholders will be used). |

*Note: Generating DOCX files requires the `python-docx` library. If missing, the script will default to PDF or exit with an error depending on usage.*

### `question_extractor/pdf_processor.py`
**Module**: Handles PDF-to-image conversion.
*   **Backends**: Supports `PyMuPDF` (recommended, fast, no external deps) and `pdf2image` (requires Poppler).
*   **Optimization**: Implements chunked processing and sticky document caching to optimize memory usage and speed.

### `question_extractor/update_summary.py`
Updates the "Number of Questions" headers and the summary table in a question bank file.
```bash
python question_extractor/update_summary.py <path_to_file>
```

### `question_extractor/clean_question_bank.py`
**Utility**: Cleans up and reformats an existing question bank file. It regroups questions by unit and topic, re-numbers them, and regenerates the summary.
```bash
python question_extractor/clean_question_bank.py [file_path]
```
*Note: Accepts an optional file path argument (defaults to 'Similarity Locus and Trigonometry questions.txt').*

### `create_checkpoint.py`
**Batch Processing**: Reads extraction manifest, sorts pages by priority (Yearly Papers > SQP > Others), and creates `checkpoint_manifest.json`.
```bash
python create_checkpoint.py
```

### `pop_batch.py`
**Batch Processing**: Retrieves the next N pages from `checkpoint_manifest.json`, removes them from the queue, and outputs them as a JSON array.
```bash
python pop_batch.py <batch_size>
# Example:
python pop_batch.py 20
```

### `question_extractor/generate_diagrams.py`
**Geometry Engine**: A script demonstrating how to programmatically generate SVG diagrams using the `FigureParser` and `FigureRenderer`. Useful for creating figure assets for papers.

### `question_extractor/test_append_feature.py`
**Testing**: Verifies the functionality of the `--append-results` feature in `extractor.py`, ensuring questions are correctly added and summaries updated.

### `generate_exam_diagrams.py`
**Standalone Tool**: Generates high-quality 3D mensuration diagrams (e.g., spheres in cylinders) that are too complex for the standard schema.
```bash
python generate_exam_diagrams.py
```

### `generate_q21_diagram.py`
**Standalone Tool**: An example of generating a specific complex geometry diagram (Q21).
*Note: This script contains hardcoded paths and is intended as a reference or template for custom diagram generation.*

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
*   **Mensuration**: `mensuration_cylinder`, `mensuration_cone`, `mensuration_sphere`.
*   **Coordinate**: `coordinate_points`, `coordinate_line`.

### Figure Renderer
The `figure_renderer.py` module uses `matplotlib` to render these schemas into PNG images which are then embedded into the generated PDF/DOCX.

---

## 🧪 Testing

The project includes several test scripts to verify core functionalities.

| Test Script | Description |
|-------------|-------------|
| `question_extractor/test_pdf_processor.py` | Verifies PDF-to-image conversion. Requires `reportlab` to generate temporary test PDFs. |
| `question_extractor/test_pdf_processor_optimization.py` | Verifies PDF processor optimizations (mocked tests). |
| `question_extractor/test_append_batch.py` | Tests the functionality of appending questions to text files while maintaining formatting. |
| `question_extractor/test_update_summary.py` | Verifies the summary update logic, ensuring counts and headers are correctly recalculated. |
| `question_extractor/test_append_feature.py` | Integration test for the `--append-results` feature in `extractor.py`. |
| `question_extractor/test_geometry_schema.py` | Unit tests for `GeometryFigure` and `FigureValidator`. |

### Running Tests

You can run individual tests using `python` or `unittest`:

```bash
# Run specific tests
python question_extractor/test_append_batch.py
python question_extractor/test_update_summary.py

# Run figure renderer internal tests
PYTHONPATH=question_extractor python question_extractor/figure_renderer.py --test
```

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
    *   **Recommendation**: Install `PyMuPDF` (`pip install PyMuPDF`). It is faster and doesn't require external tools.
    *   **Alternative**: If using `pdf2image`, you must have [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) installed and added to your system PATH.

2.  **Import Errors**:
    *   Ensure you run scripts from the **root directory** (e.g., `python question_extractor/extractor.py`, NOT `cd question_extractor && python extractor.py`).
    *   The scripts rely on relative imports based on the project root.

3.  **Hardcoded Paths**:
    *   Some utility scripts (like `clean_question_bank.py`, `identify_chapters.py`, `create_checkpoint.py`) may contain hardcoded paths or assumptions about directory structure. Always check the script source before running.

4.  **Matplotlib / Geometry Errors**:
    *   If figure rendering fails, ensure `matplotlib` is installed (`pip install matplotlib`).
    *   If using a headless environment (like a server), the renderer automatically uses the 'Agg' backend.
