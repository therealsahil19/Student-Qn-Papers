import re
import os
from datetime import datetime

def update_summary():
    file_path = 'Commercial_Math_Questions.txt'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define section boundaries
    sections = {
        'Banking': r'Topic: Banking\nNumber of Questions: \d+',
        'GST': r'Topic: GST\nNumber of Questions: \d+',
        'Shares': r'Topic: Shares and Dividends\nNumber of Questions: \d+'
    }

    # Find section content
    banking_start = content.find('Topic: Banking')
    gst_start = content.find('Topic: GST')
    shares_start = content.find('Topic: Shares and Dividends')
    summary_start = content.find('SUMMARY')

    if any(pos == -1 for pos in [banking_start, gst_start, shares_start, summary_start]):
        print("Error: Could not find all section headers in the file.")
        return

    # Extract strings for counting
    banking_text = content[banking_start:gst_start]
    gst_text = content[gst_start:shares_start]
    shares_text = content[shares_start:summary_start]

    # Count questions (looking for Q follow by number at start of line)
    def count_qs(text):
        return len(re.findall(r'^Q\d+', text, re.MULTILINE))

    counts = {
        'Banking': count_qs(banking_text),
        'GST': count_qs(gst_text),
        'Shares': count_qs(shares_text)
    }

    total = sum(counts.values())

    # 1. Update individual section headers
    content = re.sub(r'Topic: Banking\nNumber of Questions: \d+', 
                    f'Topic: Banking\nNumber of Questions: {counts["Banking"]}', content)
    content = re.sub(r'Topic: GST\nNumber of Questions: \d+', 
                    f'Topic: GST\nNumber of Questions: {counts["GST"]}', content)
    content = re.sub(r'Topic: Shares and Dividends\nNumber of Questions: \d+', 
                    f'Topic: Shares and Dividends\nNumber of Questions: {counts["Shares"]}', content)

    # 2. Update Header
    content = re.sub(r'Total questions: \d+', f'Total questions: {total}', content)
    content = re.sub(r'Extracted at: \d{4}-\d{2}-\d{2} \d{2}:\d{2}', 
                    f'Extracted at: {datetime.now().strftime("%Y-%m-%d %H:%M")}', content)

    # 3. Update Summary at bottom
    summary_pattern = r'SUMMARY\s*={70}\n(.*?)\n={70}'
    summary_replacement = (
        f"  Banking: {counts['Banking']} questions\n"
        f"  GST: {counts['GST']} questions\n"
        f"  Shares and Dividends: {counts['Shares']} questions\n"
        f"  Total questions: {total}"
    )
    
    # We need to use re.DOTALL to match across lines but be careful with the replacement
    new_summary_section = f"SUMMARY\n{'='*70}\n{summary_replacement}\n{'='*70}"
    content = re.sub(r'SUMMARY\n={70}\n.*?\n={70}', new_summary_section, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Summary Updated Successfully!")
    print(f"Total Questions: {total}")
    for k, v in counts.items():
        print(f"  - {k}: {v}")

if __name__ == "__main__":
    update_summary()
