import json
import re

def get_priority(source_paper):
    # Priority 1: Yearly papers (2016-2025)
    if re.match(r'^20[12][0-9]$', source_paper):
        return 1
    # Priority 2: SQP papers
    if 'SQP' in source_paper:
        return 2
    # Priority 3: Others
    return 3

with open('question_extractor/images_class_10/extraction_manifest.json', 'r') as f:
    data = json.load(f)

pages = data['pages']

# Sort pages based on priority
# We use a tuple (priority, source_paper, page_number) for stable sorting
pages.sort(key=lambda p: (get_priority(p['source_paper']), p['source_paper'], p['page_number']))

# Save to checkpoint
with open('checkpoint_manifest.json', 'w') as f:
    json.dump(pages, f, indent=2)

print(f"Checkpoint created with {len(pages)} pages sorted by priority.")
