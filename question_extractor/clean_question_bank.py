import re
import os

def clean_file(file_path):
    questions = {
        "Loci": [],
        "Similarity": [],
        "Trigonometry": []
    }

    current_cat = None
    current_q = []
    
    # Simple state machine to extract questions
    # A question starts with Q[digit] or Q[digit]([letter])
    # And ends before the next Q... or before a line of dashes/headers
    
    q_start_pattern = re.compile(r'^Q\d+')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            
            # Detect category changes in the existing mess
            if "Topic: Loci" in line:
                current_cat = "Loci"
                continue
            elif "Topic: Similarity" in line:
                current_cat = "Similarity"
                continue
            elif "Topic: Trigonometry" in line:
                current_cat = "Trigonometry"
                continue

            # If we find a question marker
            if q_start_pattern.match(stripped):
                if current_q and current_cat:
                    questions[current_cat].append("".join(current_q).strip())
                current_q = [line]
            elif stripped == "----------------------------------------" or "====================" in line or "UNIT:" in line or "Topic:" in line or "Number of Questions:" in line:
                if current_q and current_cat:
                    questions[current_cat].append("".join(current_q).strip())
                    current_q = []
            else:
                if current_q:
                    current_q.append(line)
                
    # Append the last one
    if current_q and current_cat:
        questions[current_cat].append("".join(current_q).strip())

    # Build the new file
    output = []
    output.append("======================================================================")
    output.append("ICSE CLASS 10 MATHEMATICS - EXTRACTED QUESTION BANK")
    output.append("======================================================================")
    output.append("Extracted at: 2026-02-01 15:52")
    
    total_q = sum(len(q) for q in questions.values())
    output.append(f"Total questions: {total_q}")
    output.append("======================================================================\n")

    # Group Units
    units = {
        "GEOMETRY": ["Loci", "Similarity"],
        "TRIGONOMETRY": ["Trigonometry"]
    }

    for unit_name, topics in units.items():
        output.append("======================================================================")
        output.append(f"UNIT: {unit_name}")
        output.append("======================================================================\n")
        
        for topic in topics:
            output.append("--------------------------------------------------")
            output.append(f"Topic: {topic}")
            output.append(f"Number of Questions: {len(questions[topic])}")
            output.append("--------------------------------------------------\n")
            
            for q_text in questions[topic]:
                output.append(q_text)
                output.append("\n    ----------------------------------------\n")
            
            output.append("\n")

    output.append("======================================================================")
    output.append("CUMULATIVE SUMMARY")
    output.append("======================================================================")
    output.append(f"  Loci: {len(questions['Loci'])} questions")
    output.append(f"  Similarity: {len(questions['Similarity'])} questions")
    output.append(f"  Trigonometry: {len(questions['Trigonometry'])} questions")
    output.append(f"  Total questions: {total_q}")
    output.append("======================================================================")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

    print(f"Cleaned up {file_path}")
    print(f"Total: {total_q} (L: {len(questions['Loci'])}, S: {len(questions['Similarity'])}, T: {len(questions['Trigonometry'])})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean and structure the question bank text file.")
    parser.add_argument("file_path", nargs='?', default='Similarity Locus and Trigonometry questions.txt', 
                        help="Path to the question bank file (default: 'Similarity Locus and Trigonometry questions.txt')")
    
    args = parser.parse_args()
    
    if os.path.exists(args.file_path):
        clean_file(args.file_path)
    else:
        print(f"Error: File '{args.file_path}' not found.")
