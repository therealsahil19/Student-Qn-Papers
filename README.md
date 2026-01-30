# 📚 Student Question Papers & Exam Generator FrameWork

A robust, modular framework for managing mathematics question banks, extracting content from PDFs via AI, and generating professional exam papers. This system supports specialized workflows for **ICSE Class 10** and **Class 8**.

## 🚀 System Architecture

```mermaid
graph TD
    PDF[Source PDF Papers] -->|extract_class8_images.py| IMG[Page Images]
    PDF -->|extractor.py| IMG
    IMG -->|extractor.py + AI| TXT[Question Bank (.txt)]
    TXT -->|update_summary.py| STATS[Updated Statistics]
    
    subgraph "Exam Generation"
        TXT -->|paper_generator.py| DOC[Class 10 PDF/DOCX]
        TXT -->|create_class8_pdf.py| C8DOC[Class 8 Term Paper]
    end
    
    subgraph "Geometry Engine"
        SCHEMA[geometry_schema.py] --> RENDER[figure_renderer.py]
        GEN3D[generate_exam_diagrams.py] --> RENDER
        RENDER --> DOC
    end
```

---

## 📂 Repository Structure

- `question_extractor/`: **Core Framework**
    - `extractor.py`: The swiss-army knife for PDF processing and prompt generation.
    - `paper_generator.py`: Generic exam paper builder (PDF/Word).
    - `figure_renderer.py`: Matplotlib-based engine for 2D/3D geometry figures.
    - `geometry_schema.py`: Data models for geometric elements (Circles, Tangents, etc.).
    - `update_summary.py`: Maintenance script to recount questions.
    - `configs/`: JSON configuration files for syllabus definitions.
    - `create_class8_pdf.py`: **[Specialized]** Custom parser for Class 8 term papers.
    - `extract_class8_images.py`: **[Specialized]** Batch image extractor for Class 8 chapters.
- `generate_exam_diagrams.py`: **[Standalone]** Script to generate complex 3D mensuration diagrams (spheres in cylinders, etc.).
- `identify_chapters.py`: **[Utility]** Helper to read PDF headers for identification.
- `Aqsa Class 8 papers/` & `Class 10pdfs/`: Raw source data.

---

## 🛠️ Workflows

### Workflow A: Standard ICSE Class 10 (Generic)

This is the primary workflow for building topic-wise question banks.

1.  **Preparation**:
    ```powershell
    # Extract images from a specific paper
    python question_extractor/extractor.py --pdf "Class 10pdfs/icse/2024.pdf" --prepare-images "./images/icse_2024"
    ```

2.  **AI Extraction**:
    ```powershell
    # Generate a prompt tailored to specific topics
    python question_extractor/extractor.py --generate-prompt --topics "GST,Banking"
    ```
    *Copy the prompt and images to your AI assistant to get structured JSON/Text output.*

3.  **Bank Management**:
    Append the extracted questions to files like `Commercial_Math_Questions.txt`. Use the `update_summary.py` script to keep counts in sync.

4.  **Paper Generation**:
    ```powershell
    # Generate a test paper from the bank
    python question_extractor/paper_generator.py --input Commercial_Math_Questions.txt --output test_paper.pdf
    ```

### Workflow B: Class 8 (Specialized)

A streamlined workflow for processing R.D. Sharma chapters and specific term papers.

1.  **Batch Extraction**:
    Use `extract_class8_images.py` to automatically process all 27 chapters of the Class 8 textbook.
    ```powershell
    python question_extractor/extract_class8_images.py
    ```
    *Auto-skips already processed chapters.*

2.  **Term Paper Generation**:
    Class 8 papers often have a custom "Section A/B/C" format embedded in a single text file.
    ```powershell
    # Parses 'Class8_Mathematics_Term_Paper.txt' and generates a PDF
    python question_extractor/create_class8_pdf.py
    ```

---

## 🔧 Script Reference Manual

### 1. `question_extractor/extractor.py`
The main entry point for extraction tasks.
- `--list-topics`: Show all available topics from config.
- `--pdf [PATH]`: Input PDF file.
- `--prepare-images [DIR]`: Convert PDF pages to images in the specified folder.
- `--generate-prompt`: Create a context-aware prompt for LLM extraction.
- `--profile [NAME]`: Switch between `class_10` (default) and `class_8`.

### 2. `question_extractor/paper_generator.py`
Generates professional exam papers.
- `--input [FILE]`: Path to question bank text file.
- `--output [FILE]`: output filename (ends in .pdf or .docx).
- `--format [pdf|docx]`: Explicitly set format.
- `--topics "Topic1,Topic2"`: Filter questions to only these topics.
- `--render-figures`: Enable/Disable geometry diagram rendering.

### 3. `generate_exam_diagrams.py`
A standalone utility for creating complex, high-quality 3D geometric figures that are too complex for the standard schema.
- **Run**: `python generate_exam_diagrams.py`
- **Output**: Generates images in `images/` folder (e.g., `iron_pole.png`, `spheres_in_cylinder.png`).
- **Features**: Handles z-ordering, hidden lines, and shading for Mensuration problems.

### 4. `question_extractor/update_summary.py`
Maintenance tool to ensure the "Number of Questions" headers in your text files match the actual content.
- **Run**: `python question_extractor/update_summary.py "path/to/questions.txt"`
- **Features**: Updates individual topic counts, total counts, and the summary table at the bottom of the file.

### 5. `identify_chapters.py`
Simple utility to peek at the first few lines of a PDF to help identify unmatched files.
- **Run**: `python identify_chapters.py` (Edit the `files` list inside the script first).

---

## 🎨 Geometry & Figure Engine

The project uses a custom schema to describe and render geometry figures.

### The `[FIGURE]` Block
Embed this block inside any question in your `.txt` files.

```yaml
[FIGURE]
type: circle_tangent
description: Circle center O, Tangent PT at T.
elements:
  - circle: {center: O, radius: 3}
  - tangent: {circle: O, point: T, external_point: P}
  - angle: {vertex: T, rays: [A, P], value: "30deg", marked: true}
given_values:
  radius: "3cm"
[/FIGURE]
```

### Supported Types (`geometry_schema.py`)
- **Circles**: `circle_chord`, `circle_tangent`, `cyclic_quadrilateral`, `alternate_segment`.
- **Triangles**: `similar_triangles`, `bpt_triangle` (Basic Proportionality).
- **Constructions**: `construction_circumcircle`, `construction_incircle`, `construction_locus`.
- **Mensuration**: `mensuration_cylinder`, `mensuration_cone` (See `generate_exam_diagrams.py` for advanced 3D).

### Rendering Engine (`figure_renderer.py`)
Uses `matplotlib` to render these schemas into high-DPI images for the PDF generator. It handles:
- Automatic axis scaling.
- Point labeling (automatic placement to avoid overlap).
- Styling (dashed lines for construction/hidden edges).

---

## ⚙️ Configuration (`question_extractor/configs/`)

The behavior of the extractor and prompt generator is driven by JSON files.

- **`class_10.json`**: The master syllabus for ICSE 2026.
    - Defines Units (Commercial Math, Algebra, etc.).
    - Defines Topics within units (GST, Banking).
    - `keywords`: Used by `extractor.py` to prompt the AI on what to look for.
    - `formulas`: Included in prompts to help the AI identify question types.

- **`class_8.json`**: Simplified syllabus for Class 8.
    - Topics: Profit/Loss, Interest, Algebraic Identities, etc.
    - Used when running `extractor.py --profile class_8`.

---

## 📦 Dependencies

Ensure you have the required Python packages:

```txt
PyMuPDF       # PDF -> Image conversion
matplotlib    # Geometry rendering
reportlab     # PDF generation
python-docx   # Word doc generation
PyYAML        # Parsing [FIGURE] blocks
```
