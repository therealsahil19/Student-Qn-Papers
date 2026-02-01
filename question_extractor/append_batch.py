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
    
    new_content = content
    
    for cat, qs in categories.items():
        if not qs: continue
        
        # Find the start of the section and the end (before next topic or summary)
        section_pattern = f"Topic: {cat}"
        start_idx = new_content.find(section_pattern)
        if start_idx == -1: continue
        
        # Find where to append - either before the next "Topic:" or before "CUMULATIVE SUMMARY"
        next_topic = new_content.find("Topic:", start_idx + 1)
        summary_start = new_content.find("CUMULATIVE SUMMARY", start_idx + 1)
        
        insert_pos = -1
        if next_topic != -1 and (summary_start == -1 or next_topic < summary_start):
            insert_pos = next_topic
        elif summary_start != -1:
            insert_pos = summary_start
        else:
            insert_pos = len(new_content)
            
        # Format questions
        # Note: We don't have global Q numbers across batches here easily, 
        # but the main file seems to use local batch numbers or just Q markers.
        # Let's see how they are formatted in the file.
        
        formatted_qs = ""
        for i, q in enumerate(qs, 1):
            formatted_qs += f"\nQ{i} (Marks {q['marks']}) ({q['paper']})\n{q['question']}\n"
            
        new_content = new_content[:insert_pos].strip() + "\n" + formatted_qs + "\n\n" + new_content[insert_pos:]
        
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Appended {len(questions)} questions from {json_file} to {target_file}")

if __name__ == "__main__":
    append_batch('temp_results_batch_10.json', 'Similarity Locus and Trigonometry questions.txt')
