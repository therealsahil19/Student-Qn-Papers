import json
import os
import mmap
import shutil

# Set of ASCII whitespace bytes (integers)
# Space (32), Tab (9), LF (10), VT (11), FF (12), CR (13)
ASCII_WS = set(b' \t\n\r\x0b\x0c')


def append_batch(json_file, target_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Separate by categories
    categories = {}
    for q in questions:
        cat = q['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    
    # Check target file size
    if not os.path.exists(target_file):
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write("")

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content into sections
    # Using regex to robustly find sections
    # Pattern: (Topic: Name\n...content...)
    # But we need to preserve everything to reconstruct it perfectly.
    
    # Strategy: Find all "Topic: <Name>" occurrences
    import re
    topic_pattern = re.compile(r'(Topic:\s*(.+?))\s*\n')
    
    matches = list(topic_pattern.finditer(content))
    
    # We will build the new content
    new_content_parts = []
    last_idx = 0
    
    # Map from topic name (normalized) to insertion data
    # Insertion data needs to be added *before* the next section starts
    
    # To do this safely:
    # 1. Identify all section starts.
    # 2. Identify the "Cumulative Summary" or end of file.
    # 3. For each section, find its end (start of next section or summary).
    # 4. Insert new questions at the end of the section.
    
    # Let's create a list of spans: (start, end, topic_name)
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        topic_name = match.group(2).strip()
        
        # End is start of next match or CUMULATIVE SUMMARY or EOF
        end = len(content)
        
        # Check for next topic
        if i + 1 < len(matches):
            end = matches[i+1].start()
            
        # Check for summary
        summary_match = re.search(r'CUMULATIVE SUMMARY', content[start:])
        if summary_match:
            summary_abs_start = start + summary_match.start()
            if summary_abs_start < end:
                end = summary_abs_start
        
        sections.append({
            'start': start,
            'end': end,
            'name': topic_name,
            'header_end': match.end()
        })
        
    # Sort insertions by topic
    # We iterate through existing sections and append relevant questions
    
    current_pos = 0
    final_output = []
    
    for section in sections:
        # Add content up to the end of this section
        # actually, simply appending the original content chunk is easiest
        
        # We need to insert *inside* this section, specifically at the end.
        # content[section['start']:section['end']] contains the whole section body.
        
        section_content = content[section['start']:section['end']]
        
        # Check if we have questions for this topic
        topic_questions = categories.get(section['name'])
        
        if topic_questions:
            # Prepare questions text
            qs_text_list = []
            for i, q in enumerate(topic_questions, 1):
                # Format: 
                # Q{i} (Marks {m}) ({paper})
                # {question}
                #
                qs_text = f"\nQ{i} (Marks {q['marks']}) ({q['paper']})\n{q['question']}\n"
                qs_text_list.append(qs_text)
            
            new_qs_block = "".join(qs_text_list)
            
            # Append before the next section starts.
            # We must be careful about whitespace.
            # section_content usually ends with newlines.
            
            combined = section_content.rstrip() + "\n" + new_qs_block + "\n"
            
            # We append content from current_pos to section['start'] (should be empty if we iterate strictly)
            # wait, current_pos concept is better.
            
            # Add pre-section content (e.g. file header)
            final_output.append(content[current_pos:section['start']])
            
            final_output.append(combined)
            current_pos = section['end']
            
            # Remove from categories to mark as done (optional, if we want to report unused)
            pass
            
        else:
            # No new questions, just copy the section as is
            final_output.append(content[current_pos:section['end']])
            current_pos = section['end']

    # Append remaining content (e.g. Cumulative Summary)
    final_output.append(content[current_pos:])
    
    new_full_content = "".join(final_output)
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_full_content)

    print(f"Appended {len(questions)} questions from {json_file} to {target_file}")

# Remove unused helper functions


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Append batch results to question bank")
    parser.add_argument("source", help="Source JSON file")
    parser.add_argument("target", help="Target text file")
    args = parser.parse_args()
    
    append_batch(args.source, args.target)
