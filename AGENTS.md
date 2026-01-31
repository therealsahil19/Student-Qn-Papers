# Agent Protocol: Automated Question Extraction

This document outlines the strict protocol for Antigravity (the Agent) to autonomously extract questions from PDF exam papers.

## 🚀 Workflow Overview

1.  **Preparation**: Agent uses `extractor.py` to convert PDF to images and generate a "manifest".
2.  **Execution Loop**: Agent iterates through the manifest, using its internal Vision capabilities to extract questions from each image.
3.  **Completion**: Agent saves the extracted questions to a text file.

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

### Step 3: The Extraction Loop (The "Self-Analysis")

For each page in `manifest['pages']`:

1.  **View the Image**: Use `view_image` (or equivalent tool) to look at `page['image_path']`.
2.  **Analyze**: Apply the `manifest['extraction_prompt']` to the image.
    *   *Constraint*: You MUST extract strictly in the JSON format requested by the prompt.
3.  **Record**: Append the extracted JSON for that page to a local results list.

### Step 4: Finalize and Save

Once all pages are processed:
1.  Combine all extracted questions into a single valid JSON list or Text block.
2.  Write the final output to the target question bank file (e.g., `Geometry_Questions.txt`).

---

## ⚠️ Critical Rules for Antigravity

1.  **NO HUMAN INTERVENTION**: You are responsible for the entire loop. Do not ask the user to "copy-paste" anything.
2.  **USE THE PROMPT**: The `extractor.py` tool generates a highly specific, context-aware prompt (containing syllabus keywords). You MUST use this prompt for your analysis to ensure accuracy.
3.  **BATCH PROCESSING**: If processing takes time, process pages in chunks (e.g., 5 at a time) and save progress, but aim for a complete run.
