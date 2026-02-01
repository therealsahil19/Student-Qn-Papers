import json
import sys

batch_size = int(sys.argv[1])
with open('checkpoint_manifest.json', 'r') as f:
    items = json.load(f)

batch = items[:batch_size]
remaining = items[batch_size:]

with open('checkpoint_manifest.json', 'w') as f:
    json.dump(remaining, f, indent=2)

print(json.dumps(batch))
