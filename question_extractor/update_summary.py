import re
import os
import sys
from datetime import datetime
from pathlib import Path

def update_file_summary(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    summary_start = content.find('SUMMARY')
    if summary_start == -1:
        # Check if there is a "BATCH \d SUMMARY" or "CUMULATIVE SUMMARY"
        summary_start = content.find('CUMULATIVE SUMMARY')
        if summary_start == -1:
            print(f"Error: Could not find SUMMARY section in {file_path}.")
            return

    # Extract sections and count questions
    counts = {}
    
    # Simple counting strategy: Find all Q[Number] at start of lines in the whole file
    # This might double count if there are multiple batches, so we'll be more precise
    # if the file has Batch summaries.
    
    # Find the very last summary section to update
    summary_matches = list(re.finditer(r'(SUMMARY|CUMULATIVE SUMMARY)\s*(=+|-+)\n', content))
    if not summary_matches:
         print(f"Error: Could not find SUMMARY section in {file_path}.")
         return
    
    last_summary_match = summary_matches[-1]
    last_summary_pos = last_summary_match.start()

    # For simplicity and robustness across different file structures:
    # We will look for all Q[Num] markers that appear BEFORE the last summary
    main_content = content[:last_summary_pos]
    
    # Split by topic to get individual counts
    topic_positions = []
    for m in re.finditer(r'Topic: (.*?)\n', main_content):
        topic_positions.append((m.start(), m.group(1)))

    if not topic_positions:
        print(f"Warning: No topic headers found in {file_path}. Topic headers should match 'Topic: [Name]'")
        return
    
    topic_positions.sort()
    
    for i in range(len(topic_positions)):
        start_pos = topic_positions[i][0]
        end_pos = topic_positions[i+1][0] if i+1 < len(topic_positions) else last_summary_pos
        topic_name = topic_positions[i][1]
        
        section_text = main_content[start_pos:end_pos]
        # Count unique Q markers (to handle cases where a question is repeated in different batches if that happens)
        # In these files, Q numbers are unique per batch.
        q_matches = re.findall(r'^Q[\d\w\(\)]+', section_text, re.MULTILINE)
        counts[topic_name] = counts.get(topic_name, 0) + len(q_matches)

    total = sum(counts.values())

    # Update individual section headers if they have "Number of Questions: \d+"
    def replace_count(match):
        prefix = match.group(1)
        topic_name = match.group(2)
        if topic_name in counts:
            return f"{prefix}{counts[topic_name]}"
        return match.group(0)

    pattern = r'(Topic: (.*?)\nNumber of Questions: )\d+'
    content = re.sub(pattern, replace_count, content)

    # Update Global Headers
    content = re.sub(r'Total questions: \d+', f'Total questions: {total}', content)
    content = re.sub(r'Extracted at: \d{4}-\d{2}-\d{2} \d{2}:\d{2}', 
                    f'Extracted at: {datetime.now().strftime("%Y-%m-%d %H:%M")}', content)
    content = re.sub(r'Last Updated: .*', f'Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', content)

    # Update the last summary section
    summary_replacement = ""
    for topic in sorted(counts.keys()):
        summary_replacement += f"  {topic}: {counts[topic]} questions\n"
    summary_replacement += f"  Total questions: {total}"

    # Re-find the last summary section as offsets might have changed
    summary_matches = list(re.finditer(r'(SUMMARY|CUMULATIVE SUMMARY)\s*(=+|-+)\n', content))
    if summary_matches:
        last_summary_pos = summary_matches[-1].start()
    
    # Detect the separator used in the summary (= or -)
    sep_match = re.search(r'(SUMMARY|CUMULATIVE SUMMARY)\s*\n(=+|-+)\n', content[last_summary_pos:])
    if sep_match:
        sep = sep_match.group(2)
        header_type = sep_match.group(1)
        new_summary_section = f"{header_type}\n{sep}\n{summary_replacement}\n{sep}"
        # Replace the section between two separators
        content = re.sub(rf'{header_type}\s*\n{re.escape(sep)}\n.*?\n{re.escape(sep)}', 
                        new_summary_section, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Summary Updated Successfully for {os.path.basename(file_path)}!")
    print(f"Total Questions: {total}")
    for k, v in sorted(counts.items()):
        print(f"  - {k}: {v}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            update_file_summary(arg)
    else:
        # Default to the existing file if no args
        update_file_summary('Commercial_Math_Questions.txt')

