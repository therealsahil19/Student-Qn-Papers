import fitz
import sys

def get_pdf_title(path):
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        doc.close()
        return text.split('\n')[0:5] # Return first 5 lines
    except Exception as e:
        return str(e)

files = [
    r"c:\Users\mehna\OneDrive\Desktop\Student Qn papers\Aqsa Class 8 papers\Mathematics Class VIII Chap9.pdf",
    r"c:\Users\mehna\OneDrive\Desktop\Student Qn papers\Aqsa Class 8 papers\Mathematics Class VIII Chap10.pdf",
    r"c:\Users\mehna\OneDrive\Desktop\Student Qn papers\Aqsa Class 8 papers\Mathematics Class VIII Chap11.pdf"
]

for f in files:
    print(f"File: {f}")
    print(get_pdf_title(f))
    print("-" * 20)
