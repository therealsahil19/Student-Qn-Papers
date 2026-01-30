import sys
import os
import re
from paper_generator import ExamPaper, Section, Question, PDFPaperGenerator

def parse_term_paper(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create Exam Paper
    paper = ExamPaper(
        title="Direct and Inv, Linear Eqn",
        subtitle="",
        duration="2 Hours",
        total_marks=80
    )
    paper.instructions = []

    # Parsing Logic
    sections_raw = re.split(r'SECTION ([A-C]) \((\d+) Marks\)', content)
    
    sections = []
    for i in range(1, len(sections_raw), 3):
        sec_char = sections_raw[i]
        sec_marks = int(sections_raw[i+1])
        sec_content = sections_raw[i+2]
        
        section_obj = Section(
            name=f"Section {sec_char}",
            description="Attempt all questions from this Section.",
            total_marks=sec_marks
        )
        
        # Split by "Question \d"
        q_splits = re.split(r'(Question \d+)', sec_content)
        for k in range(1, len(q_splits), 2):
            q_num_text = q_splits[k].strip()
            q_body = q_splits[k+1].strip()
            
            # Clean up MCQ options to be tighter for Section A
            if sec_char == 'A':
                # Identify sub-questions (i), (ii) and their options (a), (b), (c), (d)
                sub_qs = re.split(r'(\([ivxl]+\))', q_body)
                new_parts = []
                if sub_qs[0].strip():
                    new_parts.append(sub_qs[0].strip())
                
                for m in range(1, len(sub_qs), 2):
                    q_idx = sub_qs[m]
                    q_text_block = sub_qs[m+1]
                    
                    # Extract the question text and options separately
                    option_matches = list(re.finditer(r'(\([a-d]\))\s*([^\(]+)', q_text_block))
                    if option_matches:
                        # Get question text (everything before first option)
                        txt = q_text_block[:option_matches[0].start()].strip()
                        opts = [f"{m.group(1)} {m.group(2).strip()}" for m in option_matches]
                        
                        # Arrange options horizontally: (a) ... (b) ... \n (c) ... (d) ...
                        # We use padding for clear separation
                        row1 = f"{opts[0]:<35} {opts[1]}" if len(opts) >= 2 else (opts[0] if opts else "")
                        row2 = f"{opts[2]:<35} {opts[3]}" if len(opts) >= 4 else (opts[2] if len(opts) >= 3 else "")
                        
                        formatted_q = f"{q_idx} {txt}\n    {row1}\n    {row2}"
                        new_parts.append(formatted_q)
                    else:
                        new_parts.append(f"{q_idx}{q_text_block}")
                
                q_body = '\n'.join(new_parts)
                q_marks = 10
            else:
                q_marks = 0 # Marks are in individual parts
            
            question_obj = Question(
                number=q_num_text,
                marks=q_marks,
                difficulty="medium",
                topic="Mathematics",
                text=q_body
            )
            section_obj.questions.append(question_obj)
        sections.append(section_obj)

    paper.sections = sections

    # Generate
    generator = PDFPaperGenerator(render_figures=False)
    # Customize the filename to avoid confusion
    output_path = "c:/Users/mehna/OneDrive/Desktop/Student Qn papers/Class8_Mathematics_Term_Paper.pdf"
    generator.generate(paper, output_path)

if __name__ == "__main__":
    # Path to the text file we just made
    text_file = "c:/Users/mehna/OneDrive/Desktop/Student Qn papers/Class8_Mathematics_Term_Paper.txt"
    parse_term_paper(text_file)
