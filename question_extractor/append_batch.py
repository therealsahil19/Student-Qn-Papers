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
    categories = {
        "Loci": [],
        "Similarity": [],
        "Trigonometry": []
    }
    
    for q in questions:
        cat = q['category']
        if cat in categories:
            categories[cat].append(q)
    
    # Check target file size
    if not os.path.exists(target_file):
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write("")

    file_size = os.path.getsize(target_file)

    # Identify insertions
    insertions = []
    
    with open(target_file, 'rb') as f:
        if file_size == 0:
            mm = b""
        else:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        try:
            for cat, qs in categories.items():
                if not qs: continue

                cat_bytes = cat.encode('utf-8')
                section_pattern = b"Topic: " + cat_bytes

                if isinstance(mm, bytes):
                    start_idx = -1
                else:
                    start_idx = mm.find(section_pattern)

                if start_idx == -1: continue

                next_topic = mm.find(b"Topic:", start_idx + 1)
                summary_start = mm.find(b"CUMULATIVE SUMMARY", start_idx + 1)

                insert_pos = -1
                if next_topic != -1 and (summary_start == -1 or next_topic < summary_start):
                    insert_pos = next_topic
                elif summary_start != -1:
                    insert_pos = summary_start
                else:
                    insert_pos = len(mm)

                formatted_qs_list = []
                for i, q in enumerate(qs, 1):
                    formatted_qs_list.append(f"\nQ{i} (Marks {q['marks']}) ({q['paper']})\n{q['question']}\n")
                formatted_qs = "".join(formatted_qs_list)

                insertions.append((insert_pos, formatted_qs))
            
            insertions.sort(key=lambda x: x[0])

            temp_file = target_file + ".tmp"
            with open(temp_file, 'w+b') as f_out:
                last_pos = 0

                for pos, qs in insertions:
                    is_first_segment = (last_pos == 0)
                    is_ws = is_segment_whitespace(mm, last_pos, pos)

                    if is_first_segment:
                        copy_segment(mm, last_pos, pos, f_out, lstrip=True, rstrip=True)
                    else:
                        if is_ws:
                            truncate_trailing_whitespace(f_out)
                        else:
                            copy_segment(mm, last_pos, pos, f_out, lstrip=False, rstrip=True)

                    qs_bytes = ("\n" + qs + "\n\n").encode('utf-8')
                    f_out.write(qs_bytes)

                    last_pos = pos

                if isinstance(mm, bytes):
                     pass
                else:
                    copy_segment(mm, last_pos, len(mm), f_out, lstrip=False, rstrip=False)

        finally:
            if hasattr(mm, 'close'):
                mm.close()

    shutil.move(temp_file, target_file)
    print(f"Appended {len(questions)} questions from {json_file} to {target_file}")

def is_segment_whitespace(mm, start, end):
    if start >= end: return True
    if isinstance(mm, bytes):
        return mm[start:end].isspace()

    CHUNK_SIZE = 1024*1024
    curr = start
    while curr < end:
        limit = min(curr + CHUNK_SIZE, end)
        chunk = mm[curr:limit]
        if not chunk.isspace():
            return False
        curr = limit
    return True

def truncate_trailing_whitespace(f):
    f.seek(0, 2)
    pos = f.tell()
    if pos == 0: return

    CHUNK_SIZE = 1024
    while pos > 0:
        read_len = min(pos, CHUNK_SIZE)
        f.seek(pos - read_len)
        chunk = f.read(read_len)

        found = False
        for i in range(len(chunk)-1, -1, -1):
            if chunk[i] not in ASCII_WS:
                new_len = (pos - read_len) + i + 1
                f.truncate(new_len)
                f.seek(0, 2)
                return
        
        pos -= read_len
    
    f.truncate(0)
    f.seek(0, 2)

def copy_segment(mm, start, end, f_out, lstrip=False, rstrip=False):
    if start >= end: return

    CHUNK_SIZE = 1024*1024
    curr = start

    if lstrip:
        while curr < end:
            limit = min(curr + CHUNK_SIZE, end)
            chunk = mm[curr:limit]

            match_start = 0
            while match_start < len(chunk) and chunk[match_start] in ASCII_WS:
                match_start += 1

            if match_start < len(chunk):
                curr += match_start
                lstrip = False
                break
            else:
                curr += len(chunk)

    if curr >= end: return

    if not rstrip:
        while curr < end:
            limit = min(curr + CHUNK_SIZE, end)
            f_out.write(mm[curr:limit])
            curr = limit
    else:
        while curr < end:
            limit = min(curr + CHUNK_SIZE, end)
            f_out.write(mm[curr:limit])
            curr = limit

        truncate_trailing_whitespace(f_out)

if __name__ == "__main__":
    append_batch('temp_results_batch_10.json', 'Similarity Locus and Trigonometry questions.txt')
