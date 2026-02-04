import json
import os

def append_batch(json_file, target_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Read existing content to find current counts/positions
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Separate by categories
    categories = {
        "Loci": [],
        "Similarity": [],
        "Trigonometry": []
    }
    
    for q in questions:
        cat = q['category']
        if cat in categories:
            categories[cat].append(q)
    
    # Identify all insertions first to avoid repeated string concatenation
    insertions = []
    
    for cat, qs in categories.items():
        if not qs: continue
        
        # Find the start of the section and the end (before next topic or summary)
        section_pattern = f"Topic: {cat}"
        start_idx = content.find(section_pattern)
        if start_idx == -1: continue
        
        # Find where to append - either before the next "Topic:" or before "CUMULATIVE SUMMARY"
        next_topic = content.find("Topic:", start_idx + 1)
        summary_start = content.find("CUMULATIVE SUMMARY", start_idx + 1)
        
        insert_pos = -1
        if next_topic != -1 and (summary_start == -1 or next_topic < summary_start):
            insert_pos = next_topic
        elif summary_start != -1:
            insert_pos = summary_start
        else:
            insert_pos = len(content)
            
        # Format questions
        # Note: We don't have global Q numbers across batches here easily, 
        # but the main file seems to use local batch numbers or just Q markers.
        # Let's see how they are formatted in the file.
        
        formatted_qs_list = []
        for i, q in enumerate(qs, 1):
            formatted_qs_list.append(f"\nQ{i} (Marks {q['marks']}) ({q['paper']})\n{q['question']}\n")
        formatted_qs = "".join(formatted_qs_list)

        insertions.append((insert_pos, formatted_qs))
            
    # Sort insertions by position
    insertions.sort(key=lambda x: x[0])

    # Build new content using a list to avoid O(N^2) string concatenation
    parts = []
    last_pos = 0

    for pos, qs in insertions:
        segment = content[last_pos:pos]

        # Emulate the original behavior: new_content[:insert_pos].strip()
        if last_pos == 0:
            segment = segment.strip()
        else:
            if not segment.strip():
                # If segment is empty or just whitespace, the previous stripped content
                # (which ends with \n\n) plus this segment would be stripped back.
                # So we remove trailing whitespace from the last added part (the \n\n).
                if parts:
                    parts[-1] = parts[-1].rstrip()
                segment = ""
            else:
                segment = segment.rstrip()

        parts.append(segment)
        parts.append("\n" + qs + "\n\n")
        last_pos = pos

    parts.append(content[last_pos:])
    new_content = "".join(parts)
        
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Appended {len(questions)} questions from {json_file} to {target_file}")

if __name__ == "__main__":
    append_batch('temp_results_batch_10.json', 'Similarity Locus and Trigonometry questions.txt')
