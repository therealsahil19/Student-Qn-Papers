# Agent Protocol: Automated Question Extraction

This document outlines the strict protocol for Antigravity (the Agent) to autonomously extract questions from PDF exam papers.

## 🚀 Workflow Overview

1.  **Preparation**: Agent uses `extractor.py` to convert PDF to images and generate a "manifest".
2.  **Execution Loop**: Agent iterates through the manifest, using its internal Vision capabilities to extract questions from each image.
3.  **Completion**: Agent saves the extracted questions to a text file using the provided CLI tool.

---

## 🛠️ Step-by-Step Protocol

### Step 1: Initialize Extraction Job

Run the extractor with the `--quiet` flag to prepare images and get the job manifest.

```bash
# Syntax
python question_extractor/extractor.py --pdf "<PATH_TO_PDF>" --prepare-images "<OUTPUT_DIR>" --quiet
python question_extractor/extractor.py --batch-manifest "<OUTPUT_DIR>" --source "<PAPER_NAME>" --quiet
```

**Example:**
```bash
python question_extractor/extractor.py --pdf "Class 10pdfs/2024.pdf" --prepare-images "./images/2024_job" --quiet
python question_extractor/extractor.py --batch-manifest "./images/2024_job" --source "ICSE 2024" --quiet
```
*Output will be the path to the generated `extraction_manifest.json`.*

### Step 2: Load the Manifest

Read the JSON file generated in Step 1.
It contains two critical pieces of information:
1.  `extraction_prompt`: The EXACT instruction you must follow when looking at images.
2.  `pages`: A list of image paths to process.

### Step 3: The Extraction Loop (Batch Processing)

**Batch Size Recommendation:** Process **20-50 pages** in memory before saving.
*Do not save after every single page. Do not save after small chunks (e.g. 5 pages) unless the document is very short.*

For each page in the current batch:
1.  **View the Image**: Use `view_image` (or equivalent tool) to look at `page['image_path']`.
2.  **Analyze**: Apply the `manifest['extraction_prompt']` to the image.
    *   *Constraint*: You MUST extract strictly in the JSON format requested by the prompt.
3.  **Record**: Append the extracted JSON for that page to a local results list (in memory).

### Step 4: Save Batch Results (AUTONOMOUSLY)

**CRITICAL**: When your batch (20-50 pages) is complete, save your progress immediately **WITHOUT ASKING FOR PERMISSION**.

1.  **Dump Results**: Write your accumulated JSON results to a temporary file (e.g., `temp_results.json`).
    ```json
    { "page_questions": [ ... your extracted questions ... ] }
    ```
2.  **Append to Bank**: Use the CLI tool to append these questions to the master file.
    ```bash
    python question_extractor/extractor.py --append-results "temp_results.json" --target "Geometry_Questions.txt" --quiet
    ```
    *This tool handles formatting, summary updates, and safe insertion automatically.*

3.  **Repeat**: Clear your local list and continue to the next batch.

---

## ⚠️ Critical Rules for Antigravity

1.  **NO HUMAN INTERVENTION**: You are responsible for the entire loop. Do not ask the user to "copy-paste" anything.
2.  **ZERO FRICTION SAVING**: You are fully authorized to write and modify the question bank files. **DO NOT ask the user for permission** to save, append, or run the python commands. Just execute them.
3.  **BATCH EFFICIENCY**: Process large chunks (20-50 pages) at a time. Small batches (e.g., 5 pages) cause unnecessary I/O overhead and friction.
4.  **USE THE PROMPT**: The `extractor.py` tool generates a highly specific, context-aware prompt (containing syllabus keywords). You MUST use this prompt for your analysis to ensure accuracy.
