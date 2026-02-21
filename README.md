# Student Question Papers & Exam Generator Framework

A robust, modular framework for managing mathematics question banks, extracting content from PDFs via AI, and generating professional exam papers. This system supports specialized workflows for **ICSE Class 10** and **Class 8**.

## 🚀 Features

*   **AI-Ready Extraction**: Convert PDF papers to images and generate optimized prompts for LLM-based question extraction.
*   **Question Bank Management**: Maintain topic-wise text files with automatic summary updating.
*   **Professional Paper Generation**: Create PDF or Word (DOCX) exam papers with proper formatting, headers, and instructions.
*   **Geometry Engine**: Render complex 2D and 3D geometric figures directly from text descriptions using a custom YAML schema.
*   **Batch Processing**: Tools for handling large sets of papers, including checkpointing and prioritization.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher
*   **Recommended**: `PyMuPDF` (Pure Python PDF processing)
    ```bash
    pip install PyMuPDF
    ```
*   **Alternative**: [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (Required only if using `pdf2image` backend).

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
    python -m question_extractor.extractor --pdf "paper.pdf" --prepare-images "./img_job" --quiet
    python -m question_extractor.extractor --batch-manifest "./img_job" --source "2024" --quiet
    ```
2.  **Self-Execution:** Agent reads `extraction_manifest.json`, which contains both the list of images and the precise instruction prompt.
3.  **Extraction:** Agent loops through the images, applying the prompt using its vision capabilities, and saves the results.

### 2. Manual Workflow (Legacy)
For users manually extracting questions using external tools.

**Step A: Extract Questions**
1.  **Prepare Images:** Convert a PDF exam paper into images.
    ```bash
    python -m question_extractor.extractor --pdf "Class 10pdfs/icse/2024.pdf" --prepare-images "./images/2024_paper"
    ```
2.  **Generate Prompt:** Create a context-aware prompt to copy-paste into an LLM.
    ```bash
    python -m question_extractor.extractor --generate-prompt --topics "GST,Banking"
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
python -m question_extractor.extractor --profile class_8 --generate-prompt
```

---

## 📦 Batch Processing & Checkpoints

For processing large volumes of papers (e.g., hundreds of pages), the system provides a checkpointing workflow to manage state and prioritize content.

### Workflow
1.  **Generate Master Manifest**:
    Run the extractor recursively on your image root.
    ```bash
    python -m question_extractor.extractor --batch-manifest "images_root" --recursive --quiet
    ```
    This creates `images_root/extraction_manifest.json`.

2.  **Create Checkpoint**:
    Sort and prioritize pages (Yearly Papers > SQP > Others) into a queue.
    ```bash
    python create_checkpoint.py
    ```
    This reads `extraction_manifest.json` and creates `checkpoint_manifest.json`.

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
The main CLI tool for PDF processing and prompt generation.

> **Note:** Run this script as a module: `python -m question_extractor.extractor`

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
| `--append-results <file>` | Append questions from JSON/Text file to a target bank. Supports atomic updates. |
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
| `--no-figures` | Disable geometry figure rendering (shows placeholder text). |

*Note: The script uses a default auto-selection logic that attempts to create a standard ICSE paper structure (10 MCQs, 5 Short Answers, 4 Long Answers). For custom structures, filter by topic manually or modify the selection logic.*

### `question_extractor/update_summary.py`
Updates the "Number of Questions" headers and the summary table in a question bank file.
*Note: This is automatically invoked when using `extractor.py --append-results`.*
```bash
python question_extractor/update_summary.py <path_to_file>
```

### `question_extractor/clean_question_bank.py`
**Utility**: Cleans up and reformats an existing question bank file.
*Warning: This script is currently hardcoded for specific geometry topics (Loci, Similarity, Trigonometry). Use with caution on other files.*
```bash
python question_extractor/clean_question_bank.py [file_path]
```

### `create_checkpoint.py`
**Batch Processing**: Reads `question_extractor/images_class_10/extraction_manifest.json` (HARDCODED PATH), sorts pages by priority (Yearly Papers > SQP > Others), and creates `checkpoint_manifest.json`.
*Note: This script is specifically configured for the Class 10 workflow.*
```bash
python create_checkpoint.py
```

### `pop_batch.py`
**Batch Processing**: Retrieves the next N pages from `checkpoint_manifest.json` (in the current directory), removes them from the queue, and outputs them as a JSON array.
```bash
python pop_batch.py <batch_size>
# Example:
python pop_batch.py 20
```

### `question_extractor/append_batch.py`
**Utility**: Performs a "smart merge" of JSON batch results into a target question bank file. Unlike `extractor.py --append-results`, this script parses the file structure and inserts questions into their specific `Topic:` sections.
```bash
python question_extractor/append_batch.py <source_json> <target_txt>
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
*   **Circles**: `circle_inscribed_angle`, `circle_tangent`, `circle_chord`, `circle_secant`, `cyclic_quadrilateral`, `alternate_segment`.
*   **Triangles**: `similar_triangles`, `congruent_triangles`, `triangle_properties`, `bpt_triangle`.
*   **Constructions**: `construction_tangent`, `construction_circumcircle`, `construction_incircle`, `construction_locus`.
*   **Coordinate Geometry**: `coordinate_points`, `coordinate_line`, `coordinate_reflection`.
*   **Mensuration**: `mensuration_cylinder`, `mensuration_cone`, `mensuration_sphere`, `mensuration_combined`.
*   **Generic**: `generic`.

### Figure Renderer
The `figure_renderer.py` module uses `matplotlib` to render these schemas into PNG images which are then embedded into the generated PDF/DOCX.

---

## 🧪 Testing

The project includes several test scripts to verify core functionalities.

| Test Script | Description |
|-------------|-------------|
| `question_extractor/test_pdf_processor.py` | Verifies PDF-to-image conversion. Requires `reportlab` to generate temporary test PDFs. |
| `question_extractor/test_pdf_processor_optimization.py` | Tests performance optimizations in PDF processing (e.g., avoiding redundant file opens). |
| `question_extractor/test_append_batch.py` | Tests the functionality of appending questions to text files while maintaining formatting. |
| `question_extractor/test_update_summary.py` | Verifies the summary update logic, ensuring counts and headers are correctly recalculated. |
| `question_extractor/test_append_feature.py` | Integration test for the `--append-results` feature in `extractor.py`. |
| `question_extractor/test_geometry_schema.py` | Unit tests for `GeometryFigure` schema validation. |
| `question_extractor/figure_renderer.py` | Can be run with `--test` to verify the figure rendering engine. |

### Running Tests

You can run individual tests using `python` or `unittest`. Ensure `PYTHONPATH` is set to the project root.

```bash
# Run specific tests
PYTHONPATH=. python question_extractor/test_append_batch.py
PYTHONPATH=. python question_extractor/test_update_summary.py

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
    *   Ensure `PyMuPDF` is installed (`pip install PyMuPDF`). It is the default and recommended backend.
    *   If using `pdf2image`, you must have [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) installed and added to your system PATH.

2.  **Import Errors**:
    *   Ensure you run scripts from the **root directory**.
    *   For `extractor.py`, use the module syntax: `python -m question_extractor.extractor`.
    *   The scripts rely on relative imports based on the project root.

3.  **Hardcoded Paths**:
    *   Some utility scripts (like `clean_question_bank.py`, `identify_chapters.py`) may contain hardcoded paths. Always check the script source before running.
