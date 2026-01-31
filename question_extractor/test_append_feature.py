
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path to allow imports if needed
sys.path.append(str(Path(__file__).parent.parent))

def test_append_feature():
    print("Running append feature test...")

    # Setup paths
    base_dir = Path(__file__).parent
    extractor_script = base_dir / "extractor.py"
    target_file = base_dir / "test_target_bank.txt"
    json_input = base_dir / "test_input.json"

    # 1. Create initial target file
    initial_content = """======================================================================
ICSE CLASS 10 MATHEMATICS - EXTRACTED QUESTION BANK
======================================================================
Extracted at: 2024-01-01 12:00
Total questions: 1
======================================================================

======================================================================
UNIT: ALGEBRA
======================================================================

--------------------------------------------------
Topic: Quadratic Equations
Number of Questions: 1
--------------------------------------------------

Q1 [3 marks] (easy)

    Solve x^2 - 4 = 0

    ----------------------------------------


======================================================================
SUMMARY
======================================================================
  Quadratic Equations: 1 questions, 3 marks
  Total questions: 1
======================================================================
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(initial_content)

    # 2. Create JSON input
    json_content = """
{
  "page_questions": [
    {
      "question_number": "2",
      "question_text": "Find the roots of x^2 - 5x + 6 = 0",
      "topic": "Quadratic_Equations",
      "unit": "Algebra",
      "marks": 3,
      "difficulty": "medium"
    },
    {
        "question_number": "3",
        "question_text": "Define a matrix.",
        "topic": "Matrices",
        "unit": "Algebra",
        "marks": 2,
        "difficulty": "easy"
    }
  ]
}
"""
    with open(json_input, "w", encoding="utf-8") as f:
        f.write(json_content)

    # 3. Run command
    cmd = [
        sys.executable,
        str(extractor_script),
        "--append-results", str(json_input),
        "--target", str(target_file),
        "--quiet"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Stderr: {e.stderr}")
        return False

    # 4. Verify content
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    print("\n--- Final File Content Preview ---")
    print(content[-500:])
    print("----------------------------------\n")

    # Check if Q2 and Q3 are present
    if "Find the roots of" not in content:
        print("FAIL: Q2 text not found")
        return False
    if "Define a matrix" not in content:
        print("FAIL: Q3 text not found")
        return False

    # Check if Summary was updated
    if "Quadratic Equations: 2 questions" not in content: # 1 initial + 1 new
        print("FAIL: Quadratic Equations count incorrect in summary")
        return False
    if "Matrices: 1 questions" not in content:
        print("FAIL: Matrices count incorrect in summary")
        return False
    if "Total questions: 3" not in content:
        print("FAIL: Total questions count incorrect")
        return False

    # Check if old Q1 is still there
    if "Solve x^2 - 4 = 0" not in content:
        print("FAIL: Original Q1 lost")
        return False

    # Cleanup
    os.remove(target_file)
    os.remove(json_input)

    print("SUCCESS: Append feature works as expected.")
    return True

if __name__ == "__main__":
    if test_append_feature():
        sys.exit(0)
    else:
        sys.exit(1)
