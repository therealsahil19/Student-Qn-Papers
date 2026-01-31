# Agent Protocol: Automated Question Extraction

This document outlines the strict protocol for Antigravity (the Agent) to autonomously extract questions from exam papers.

## 🚀 Workflow Overview

1.  **Preparation**: Agent uses `extractor.py` to generate a "Master Manifest" covering ALL images in a root directory (recursive).
2.  **Execution Loop**: Agent iterates through the master manifest, using its internal Vision capabilities to extract questions.
3.  **Completion**: Agent saves the extracted questions to a single text file autonomously.

---

## 🛠️ Step-by-Step Protocol

### Step 1: Initialize Extraction Job (Recursive Mode)

Point the tool at the **root** image directory (e.g., `images_class_10`) and use the `--recursive` flag. This will find all images in all subfolders and create one giant job list.

```bash
# Syntax
python question_extractor/extractor.py --batch-manifest "<ROOT_IMAGE_DIR>" --recursive --quiet
```

**Example:**
```bash
python question_extractor/extractor.py --batch-manifest "images_class_10" --recursive --quiet
```
*Output will be the path to the generated `extraction_manifest.json`.*

### Step 2: Load the Manifest

Read the JSON file generated in Step 1.
It contains:
1.  `extraction_prompt`: The instruction to follow.
2.  `pages`: A list of ALL pages from ALL papers found in the subdirectories.

**Note:** Each page entry in `pages` has a `source_paper` field (derived from its folder name). You will need this for Step 3.

### Step 3: The Extraction Loop (Batch Processing)

**Batch Size Recommendation:** Process **20-50 pages** in memory before saving.

For each page in the current batch:
1.  **View the Image**: Look at `page['image_path']`.
2.  **Analyze**: Apply the `manifest['extraction_prompt']` to the image.
3.  **Context Injection (CRITICAL)**:
    *   Read the `source_paper` field from the current page object in the manifest.
    *   **YOU MUST** include this value in your extracted JSON for every question.
    *   *Example JSON Output*:
        ```json
        {
          "question_number": "1(i)",
          "question_text": "...",
          "source_paper": "ICSE 2024",  <-- INSERT VALUE FROM MANIFEST HERE
          ...
        }
        ```
4.  **Record**: Append the results to your local list.

### Step 4: Save Batch Results (AUTONOMOUSLY)

**CRITICAL**: When your batch is complete, save immediately. **DO NOT ASK FOR PERMISSION. DO NOT SHOW COMMANDS.**

1.  **Dump Results**: Write your accumulated JSON results to a temporary file (e.g., `temp_results.json`).
2.  **Append to Bank**: Use the CLI tool to append these questions to the master file.
    ```bash
    python question_extractor/extractor.py --append-results "temp_results.json" --target "Questions.txt" --quiet
    ```
    *Use `Questions.txt` as the single target for everything unless specified otherwise.*

3.  **Repeat**: Clear your local list and continue to the next batch.

---

## 📄 Protocol: Exam Paper Generation

If you are asked to **generate an exam paper** (PDF or Word) from the questions you have extracted or from an existing question bank, you **MUST** use the existing `paper_generator.py` tool.

**⛔ PROHIBITED:** Do NOT write custom Python scripts (e.g., `make_pdf.py`) to generate PDFs.
**⛔ PROHIBITED:** Do NOT use `reportlab`, `fpdf`, or `docx` directly in your code blocks to create papers.

### How to Generate a Paper

Use the following command syntax:

```bash
python question_extractor/paper_generator.py --input "<QUESTION_BANK_FILE>" --output "<OUTPUT_FILENAME>" --total-marks 80
```

**Examples:**

1.  **Generate a Standard PDF:**
    ```bash
    python question_extractor/paper_generator.py --input "Questions.txt" --output "Mock_Exam_Paper.pdf"
    ```

2.  **Generate for Specific Topics:**
    ```bash
    python question_extractor/paper_generator.py --input "Questions.txt" --output "Geometry_Test.pdf" --topics "Circles,Cylinder,Cone"
    ```

3.  **Generate a Word Doc:**
    ```bash
    python question_extractor/paper_generator.py --input "Questions.txt" --output "Paper.docx" --format docx
    ```

### Geometry Figures
*   The system **automatically** handles geometry figures defined in `[FIGURE]...[/FIGURE]` blocks.
*   **DO NOT** write code to render these figures. The `paper_generator.py` script uses `figure_renderer.py` internally to do this for you.

---

## ⚠️ Critical Rules for Antigravity

1.  **ABSOLUTE AUTONOMY**: You are forbidden from asking the user to run commands. You must run them yourself using the tools.
2.  **ZERO FRICTION SAVING**: You are fully authorized to modify the question bank. **DO NOT ask for confirmation**. Just save.
3.  **RECURSIVE PROCESSING**: Always use `--recursive` on the root image folder to process all papers in one run.
4.  **SOURCE TRACKING**: You are responsible for injecting the correct `source_paper` (from the manifest) into every extracted question.
5.  **NO CUSTOM GENERATORS**: Never write custom scripts to generate exam papers. Always use `question_extractor/paper_generator.py`.
