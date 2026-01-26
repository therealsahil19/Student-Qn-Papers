# 📖 Future Extraction Guide

This guide explains how to continue extracting Commercial Mathematics questions when you add more PDF papers to the project.

## Directory Overview

- `/` : Root directory containing PDF papers.
- `/question_extractor/` : Core workspace for extraction.
    - `/images/` : Subdirectories for each paper containing page images.
    - `extractor.py` : Tool for PDF conversion and prompt generation.
    - `update_summary.py` : Utility to recount and update the summary.
    - `Commercial_Math_Questions.txt` : The final question bank.

---

## 🚀 Step-by-Step Workflow

### 1. Prepare New PDFs
1. Place your new PDF files in the root folder (or wherever you prefer).
2. Open a terminal in the `question_extractor` directory.
3. Run the following command to convert the PDF to images for analysis:
   ```powershell
   python extractor.py --pdf "../Path/To/Your/NewPaper.pdf" --prepare-images "./images/PaperName_Folder"
   ```
   *Note: Replace `Path/To/Your/NewPaper.pdf` and `PaperName_Folder` with actual names.*

### 2. Visual Analysis
1. Open the folder you created in `./images/PaperName_Folder`.
2. Look through the images for questions matching:
   - **GST** (Tax, Invoice, CGST/SGST)
   - **Banking** (Recurring Deposit, Interest, Maturity)
   - **Shares & Dividends** (Premium, Discount, Dividend Yield)

### 3. Extract & Add Questions
1. When you find a question, copy the format used in `Commercial_Math_Questions.txt`.
2. Open `Commercial_Math_Questions.txt`.
3. Locate the appropriate section (Banking, GST, or Shares).
4. Append the new question at the end of that section.
   - **Tip**: Follow the existing format exactly:
     ```
     Q[Num] [[Marks]] (Difficulty) 

         [Exact Question Text]
         Subtopic: [Specific Type]
         [Source: Name Of Paper]

         ----------------------------------------
     ```

### 4. Update Summaries
Instead of manually updating the "Number of Questions" headers and the bottom Summary table, just run the helper script:
```powershell
python update_summary.py
```
This script will:
- Scan the entire file.
- Correct the question counts for each category.
- Update the "Total questions" in the header.
- Refresh the SUMMARY table at the bottom.
- Update the "Extracted at" timestamp.

---

## 🛠️ Troubleshooting

- **PDF conversion fails?** Ensure `PyMuPDF` is installed (`pip install PyMuPDF`).
- **Images are blurry?** You can increase DPI in `pdf_processor.py` (default is 200).
- **Summary script errors?** make sure you haven't deleted the "Topic: ..." headers or the "SUMMARY" section markers, as the script relies on them.

---

## 💡 Pro Tip for AI Analysis
If you are using an AI to help you extract (like me), you can generate a tailored prompt for it using:
```powershell
python extractor.py --generate-prompt
```
This will output a detailed instruction block based on your `topics_config.json` that you can paste into your chat with an AI.
