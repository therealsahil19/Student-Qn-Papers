"""
ICSE Class 10 Math Question Extractor Framework

A framework for extracting questions from ICSE Class 10 Math papers
based on user-specified topics.

Usage:
    python extractor.py --list-topics
    python extractor.py --pdf "path/to/paper.pdf" --output "questions.txt"
    python extractor.py --pdf "path/to/paper.pdf" --topics "Quadratic Equations,Trigonometry"
"""

import json
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import glob
import sys

# Import local modules
try:
    from pdf_processor import PDFProcessor, PDFPage
    import update_summary
except ImportError:
    PDFProcessor = None
    PDFPage = None
    update_summary = None


# Compiled regex pattern for extracting JSON from Markdown code blocks
JSON_BLOCK_PATTERN = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)


@dataclass
class ExtractedQuestion:
    """Represents an extracted question from a paper."""
    question_number: str
    question_text: str
    topic: str
    unit: str = ""
    subtopic: Optional[str] = None
    marks: Optional[int] = None
    sub_parts: Optional[List[dict]] = None
    page_number: int = 0
    source_paper: str = ""
    difficulty: Optional[str] = None  # easy, medium, hard
    has_diagram: bool = False
    diagram_description: Optional[str] = None


# ... imports ...
from question_extractor.topic_manager import TopicManager
from question_extractor.prompt_generator import PromptGenerator

# ... (ExtractedQuestion dataclass remains) ...

class QuestionExtractor:
    """
    Main class for extracting questions from ICSE Math papers.
    
    This framework prepares PDFs for visual analysis and provides
    structured prompts for AI-powered question extraction.
    """
    
    def __init__(self, profile: str = "class_10", config_path: str = None):
        """
        Initialize the question extractor.
        
        Args:
            profile: Profile name (e.g., "class_10", "class_8")
            config_path: Path to topics_config.json
        """
        self.profile = profile
        self.topic_manager = TopicManager(profile, config_path)
        self.prompt_generator = PromptGenerator(self.topic_manager)
        self.pdf_processor = PDFProcessor() if PDFProcessor else None
        self.extracted_questions: List[ExtractedQuestion] = []
        self._existing_signatures = set()  # Set of (question_number, source_paper) for fast lookup
        self.processed_pages: Dict[str, List[int]] = {}  # Track processed pages per paper
        self.questions_by_paper: Dict[str, List[ExtractedQuestion]] = {} # Index for O(1) access
    
    def check_dependencies(self) -> dict:
        """Check if all dependencies are available."""
        status = {
            "pdf_processor": self.pdf_processor is not None,
            "topics_config": self.topic_manager.config_path.exists(),
        }
        
        if self.pdf_processor:
            backend_info = self.pdf_processor.get_backend_info()
            status["pdf_backend"] = backend_info["backend"]
            status["pdf_backend_available"] = backend_info["available"]
        else:
            status["pdf_backend"] = "none"
            status["pdf_backend_available"] = False
        
        return status
    
    def prepare_pdf(
        self, 
        pdf_path: str, 
        output_dir: str = None
    ) -> List[Any]:
        """
        Prepare a PDF for extraction by converting to images.
        """
        if not self.pdf_processor:
            raise RuntimeError(
                "PDF processor not available. Install PyMuPDF:\n"
                "pip install PyMuPDF"
            )
        
        return self.pdf_processor.convert_pdf_to_images(pdf_path, output_dir)
    
    def get_all_image_paths(self, images_dir: str) -> List[str]:
        """
        Get all image paths from a directory, sorted by page number.
        """
        images_dir = Path(images_dir)
        if not images_dir.exists():
            return []
        
        # Find all PNG images
        image_files = list(images_dir.glob("*.png"))
        
        # Sort by page number (extract number from filename like page_001.png)
        def get_page_num(path):
            try:
                return int(path.name.rpartition('_')[2][:-4])
            except:
                return 0
        
        image_files.sort(key=get_page_num)
        return [str(p.absolute()) for p in image_files]
    
    def generate_extraction_prompt(
        self, 
        topics: List[str] = None,
        include_examples: bool = True,
        page_number: int = None,
        is_batch_mode: bool = False
    ) -> str:
        """Type forwarding to prompt_generator."""
        return self.prompt_generator.generate_extraction_prompt(
            topics, include_examples, page_number, is_batch_mode
        )
    
    def generate_batch_extraction_manifest(
        self,
        images_dir: str,
        topics: List[str] = None,
        source_paper: str = "",
        recursive: bool = False
    ) -> Dict:
        """Type forwarding to prompt_generator."""
        return self.prompt_generator.generate_batch_extraction_manifest(
            images_dir, self.get_all_image_paths, topics, source_paper, recursive
        )
    
    def add_question(self, question: ExtractedQuestion):
        """Add an extracted question to the collection."""
        # Check for duplicates based on question number and source
        signature = (question.question_number, question.source_paper)
        if signature not in self._existing_signatures:
            self._existing_signatures.add(signature)
            self.extracted_questions.append(question)
            
            # Update index
            if question.source_paper not in self.questions_by_paper:
                self.questions_by_paper[question.source_paper] = []
            self.questions_by_paper[question.source_paper].append(question)
    
    def add_questions_from_json(
        self, 
        json_data: str, 
        source_paper: str = "",
        page_number: int = 0
    ):
        """
        Parse JSON output from AI extraction and add questions.
        
        Args:
            json_data: JSON string with extracted questions
            source_paper: Name of the source paper
            page_number: Page number for tracking
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            json_match = JSON_BLOCK_PATTERN.search(json_data)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                raise ValueError("Could not parse JSON from response")
        
        # Support both "questions" and "page_questions" keys
        questions = data.get("page_questions", data.get("questions", []))
        
        for q in questions:
            question = ExtractedQuestion(
                question_number=q.get("question_number", ""),
                question_text=q.get("question_text", ""),
                topic=q.get("topic", "Unknown"),
                unit=q.get("unit", ""),
                subtopic=q.get("subtopic"),
                marks=q.get("marks"),
                has_diagram=q.get("has_diagram", False),
                difficulty=q.get("difficulty"),
                page_number=page_number if page_number else q.get("page_number", 0),
                source_paper=q.get("source_paper", source_paper)
            )
            self.add_question(question)
        
        # Track processed pages
        if source_paper not in self.processed_pages:
            self.processed_pages[source_paper] = []
        if page_number and page_number not in self.processed_pages[source_paper]:
            self.processed_pages[source_paper].append(page_number)
        
        return len(questions)
    
    def get_extraction_progress(self, source_paper: str, total_pages: int) -> Dict:
        """
        Get extraction progress for a paper.
        
        Args:
            source_paper: Name of the paper
            total_pages: Total number of pages in the paper
            
        Returns:
            Progress dictionary
        """
        processed = self.processed_pages.get(source_paper, [])
        questions = self.questions_by_paper.get(source_paper, [])
        
        return {
            "source_paper": source_paper,
            "total_pages": total_pages,
            "pages_processed": len(processed),
            "pages_remaining": total_pages - len(processed),
            "questions_extracted": len(questions),
            "processed_page_numbers": sorted(processed),
            "completion_percentage": round(len(processed) / total_pages * 100, 1) if total_pages > 0 else 0
        }
    
    def get_questions_by_topic(self, topic: str) -> List[ExtractedQuestion]:
        """Get all extracted questions for a specific topic."""
        return [q for q in self.extracted_questions if q.topic == topic]
    
    def get_questions_by_unit(self, unit: str) -> List[ExtractedQuestion]:
        """Get all extracted questions for a specific unit."""
        return [q for q in self.extracted_questions if q.unit == unit]
    
    def get_questions_summary(self) -> dict:
        """Get summary of extracted questions by topic."""
        summary = {}
        for q in self.extracted_questions:
            if q.topic not in summary:
                summary[q.topic] = {"count": 0, "total_marks": 0, "unit": q.unit}
            summary[q.topic]["count"] += 1
            if q.marks:
                summary[q.topic]["total_marks"] += q.marks
        return summary
    
    def format_questions_to_text(self) -> str:
        """Format current extracted questions as text for the question bank."""
        lines = []

        # Group by unit, then by topic
        by_unit = {}
        for q in self.extracted_questions:
            unit = q.unit or "Other"
            if unit not in by_unit:
                by_unit[unit] = {}
            if q.topic not in by_unit[unit]:
                by_unit[unit][q.topic] = []
            by_unit[unit][q.topic].append(q)

        for unit, topics in sorted(by_unit.items()):
            lines.append("")
            lines.append("=" * 70)
            lines.append(f"UNIT: {unit.upper()}")
            lines.append("=" * 70)

            for topic, questions in sorted(topics.items()):
                lines.append("")
                lines.append("-" * 50)
                lines.append(f"Topic: {topic.replace('_', ' ')}")
                lines.append(f"Number of Questions: {len(questions)}")
                lines.append("-" * 50)
                lines.append("")

                for i, q in enumerate(questions, 1):
                    marks_str = f"[{q.marks} marks]" if q.marks else ""
                    difficulty_str = f"({q.difficulty})" if q.difficulty else ""
                    source_str = f"[Source: {q.source_paper}]" if q.source_paper else ""
                    diagram_str = "[Has Diagram]" if q.has_diagram else ""

                    lines.append(f"Q{q.question_number} {marks_str} {difficulty_str} {diagram_str}")
                    lines.append("")
                    lines.append(f"    {q.question_text}")
                    if q.has_diagram and q.diagram_description:
                        lines.append(f"    Diagram Description: {q.diagram_description}")
                    if q.subtopic:
                        lines.append(f"    Subtopic: {q.subtopic}")
                    if source_str:
                        lines.append(f"    {source_str}")
                    lines.append("")
                    lines.append("    " + "-" * 40)
                    lines.append("")

        return "\n".join(lines)

    def save_results(self, output_path: str, format: str = "txt"):
        """
        Save extracted questions to file.
        
        Args:
            output_path: Path for output file
            format: Output format (txt, json, or markdown)
        """
        output_path = Path(output_path)
        
        if format == "json":
            self._save_as_json(output_path)
        elif format == "txt":
            self._save_as_txt(output_path)
        elif format == "markdown":
            self._save_as_markdown(output_path)
        
        print(f"✓ Saved {len(self.extracted_questions)} questions to {output_path}")

    def _save_as_json(self, output_path: Path):
        """Helper to save as JSON."""
        data = {
            "extracted_at": datetime.now().isoformat(),
            "total_questions": len(self.extracted_questions),
            "summary": self.get_questions_summary(),
            "processed_pages": self.processed_pages,
            "questions": [asdict(q) for q in self.extracted_questions]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_as_txt(self, output_path: Path):
        """Helper to save as TXT."""
        board = self.topic_manager.get_syllabus_info().get('board', 'ICSE')
        class_num = self.topic_manager.get_syllabus_info().get('class', '10')
        
        lines = [
            "=" * 70,
            f"{board} CLASS {class_num} MATHEMATICS - EXTRACTED QUESTION BANK",
            "=" * 70,
            f"Extracted at: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Total questions: {len(self.extracted_questions)}",
            "=" * 70,
            ""
        ]
        
        lines.append(self.format_questions_to_text())
        
        # Summary at the end
        lines.append("")
        lines.append("=" * 70)
        lines.append("SUMMARY")
        lines.append("=" * 70)
        summary = self.get_questions_summary()
        for topic, data in sorted(summary.items()):
            lines.append(f"  {topic.replace('_', ' ')}: {data['count']} questions, {data['total_marks']} marks")
        lines.append("=" * 70)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _save_as_markdown(self, output_path: Path):
        """Helper to save as Markdown."""
        lines = [
            "# Extracted Questions",
            f"\nExtracted at: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Total questions: {len(self.extracted_questions)}\n",
            "---\n"
        ]
        
        # Group by unit, then by topic
        by_unit = {}
        for q in self.extracted_questions:
            unit = q.unit or "Other"
            if unit not in by_unit:
                by_unit[unit] = {}
            if q.topic not in by_unit[unit]:
                by_unit[unit][q.topic] = []
            by_unit[unit][q.topic].append(q)
        
        for unit, topics in sorted(by_unit.items()):
            lines.append(f"\n# {unit}\n")
            for topic, questions in sorted(topics.items()):
                lines.append(f"\n## {topic.replace('_', ' ')}\n")
                for q in questions:
                    marks_str = f" [{q.marks} marks]" if q.marks else ""
                    lines.append(f"### Q{q.question_number}{marks_str}")
                    lines.append(f"\n{q.question_text}\n")
                    if q.subtopic:
                        lines.append(f"*Subtopic: {q.subtopic}*\n")
                    if q.source_paper:
                        lines.append(f"*Source: {q.source_paper}*\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def clear_questions(self):
        """Clear all extracted questions."""
        self.extracted_questions = []
        self._existing_signatures = set()
        self.questions_by_paper = {}


def _handle_syllabus_info(extractor) -> int:
    info = extractor.topic_manager.get_syllabus_info()
    board = info.get('board', 'CISCE')
    class_num = info.get('class', '10')
    print(f"\n📚 {board} Class {class_num} Mathematics Syllabus 2026\n")
    print("-" * 50)
    print(f"Board: {info.get('board', 'CISCE')}")
    print(f"Total Marks: {info.get('total_marks', 100)}")
    print(f"Theory: {info.get('theory_marks', 80)} marks")
    print(f"Internal Assessment: {info.get('internal_assessment', 20)} marks")
    print("\nExam Pattern:")
    pattern = info.get("exam_pattern", {})
    for section, desc in pattern.items():
        print(f"  {section}: {desc}")
    print("\nNotes:")
    for note in info.get("notes", []):
        print(f"  • {note}")
    print("-" * 50)
    return 0

def _handle_list_units(extractor) -> int:
    info = extractor.topic_manager.get_syllabus_info()
    board = info.get('board', 'ICSE')
    class_num = info.get('class', '10')
    print(f"\n📖 {board} Class {class_num} Math Units\n")
    print("-" * 60)
    units = extractor.topic_manager.get_all_units()
    for key, data in units.items():
        status = "✓" if data.get("enabled", True) else "✗"
        unit_name = data.get("unit_name", key)
        weightage = data.get("weightage", "N/A")
        topics_count = len(data.get("topics", {}))
        print(f"{status} {unit_name:30} | Weightage: {weightage:12} | Topics: {topics_count}")
    print("-" * 60)
    return 0

def _handle_list_topics(extractor) -> int:
    info = extractor.topic_manager.get_syllabus_info()
    board = info.get('board', 'ICSE')
    class_num = info.get('class', '10')
    print(f"\n📚 {board} Class {class_num} Math Topics\n")
    print("-" * 70)
    all_topics = extractor.topic_manager.get_all_topics()
    enabled = extractor.topic_manager.get_enabled_topics()
    
    # Group by unit
    by_unit = {}
    for name, data in all_topics.items():
        unit = data.get("unit", "Other")
        if unit not in by_unit:
            by_unit[unit] = []
        by_unit[unit].append((name, data, name in enabled))
    
    for unit, topics in sorted(by_unit.items()):
        print(f"\n[{unit}]")
        for name, data, is_enabled in topics:
            status = "✓" if is_enabled else "✗"
            full_name = data.get("full_name", name)
            print(f"  {status} {name:30} | {full_name}")
    
    print("-" * 70)
    print(f"Total: {len(all_topics)} topics, {len(enabled)} enabled\n")
    return 0

def _handle_check(extractor) -> int:
    print("\n🔍 Dependency Check\n")
    status = extractor.check_dependencies()
    for key, value in status.items():
        icon = "✓" if value else "✗"
        print(f"  {icon} {key}: {value}")
    print()
    return 0

def _handle_topic_management(args, extractor) -> int:
    if args.enable_topic:
        if extractor.topic_manager.enable_topic(args.enable_topic):
            extractor.topic_manager.save_config()
            print(f"✓ Enabled topic: {args.enable_topic}")
        else:
            print(f"✗ Topic not found: {args.enable_topic}")
        return 0
    
    if args.disable_topic:
        if extractor.topic_manager.disable_topic(args.disable_topic):
            extractor.topic_manager.save_config()
            print(f"✓ Disabled topic: {args.disable_topic}")
        else:
            print(f"✗ Topic not found: {args.disable_topic}")
        return 0
    return 0

def _handle_prompt_generation(args, extractor) -> int:
    topics = args.topics.split(",") if args.topics else None
    prompt = extractor.generate_extraction_prompt(topics=topics, is_batch_mode=True)
    print("\n" + "=" * 60)
    print("EXTRACTION PROMPT")
    print("=" * 60)
    # Handle Windows console encoding for special characters
    try:
        print(prompt)
    except UnicodeEncodeError:
        print(prompt.encode('ascii', 'replace').decode('ascii'))
    print("=" * 60 + "\n")
    return 0

def _handle_batch_manifest(args, extractor) -> int:
    topics = args.topics.split(",") if args.topics else None
    manifest = extractor.generate_batch_extraction_manifest(
        args.batch_manifest,
        topics=topics,
        source_paper=args.source,
        recursive=args.recursive
    )

    if not args.quiet:
        print("\n📋 Batch Extraction Manifest")
        print("=" * 60)
        print(f"Source: {manifest['source_paper']}")
        print(f"Images Directory: {manifest['images_directory']}")
        print(f"Total Pages: {manifest['total_pages']}")
        print(f"Target Topics: {', '.join(manifest['target_topics'])}")
        print("\nPages to process:")
        for page in manifest['pages']:
            print(f"  Page {page['page_number']}: {page['image_path']}")
        print("=" * 60 + "\n")
    
    # Save manifest
    manifest_path = Path(args.batch_manifest) / "extraction_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    if not args.quiet:
        print(f"✓ Manifest saved to {manifest_path}")
    else:
        # Minimal output for agent
        print(str(manifest_path))
    return 0

def _handle_pdf_processing(args, extractor) -> int:
    if not args.quiet:
        print(f"📄 Processing: {args.pdf}")
    try:
        pages = extractor.prepare_pdf(args.pdf, args.prepare_images)
        if not args.quiet:
            print(f"✓ Converted {len(pages)} pages to images in {args.prepare_images}")
            for page in pages:
                print(f"  - Page {page.page_number}: {page.image_path}")
        else:
            # Minimal output for agent
            print(str(args.prepare_images))
    except Exception as e:
        if not args.quiet:
            print(f"✗ Error: {e}")
        else:
            print(f"Error: {e}")
        return 1
    return 0

def _handle_append_results(args, extractor) -> int:
    if not os.path.exists(args.append_results):
        print(f"Error: Source file {args.append_results} not found.")
        return 1

    # Read source data
    with open(args.append_results, 'r', encoding='utf-8') as f:
        source_content = f.read()

    # Try to parse as JSON first (from agent output)
    try:
        data = json.loads(source_content)
        # Handle if the input is a list of questions directly
        if isinstance(data, list):
            questions_list = data
        else:
            questions_list = data.get("page_questions", data.get("questions", []))
        
        for q in questions_list:
            question = ExtractedQuestion(
                question_number=q.get("question_number", ""),
                question_text=q.get("question_text", ""),
                topic=q.get("topic", "Unknown"),
                unit=q.get("unit", ""),
                subtopic=q.get("subtopic"),
                marks=q.get("marks"),
                has_diagram=q.get("has_diagram", False),
                diagram_description=q.get("diagram_description"),
                difficulty=q.get("difficulty"),
                page_number=q.get("page_number", 0),
                source_paper=q.get("source_paper", "")
            )
            extractor.add_question(question)
        
        # Format questions using the same style as save_results
        text_to_append = extractor.format_questions_to_text()
    except (ValueError, json.JSONDecodeError):
        # Assume it's already formatted text
        text_to_append = source_content

    target_path = Path(args.target).resolve()
    try:
        cwd = Path.cwd().resolve()
        if not target_path.is_relative_to(cwd):
             # Try fallback check for some python versions/environments
             if not str(target_path).startswith(str(cwd)):
                print(f"Error: Target path must be within the current working directory: {cwd}")
                return 1
    except ValueError:
         if not str(target_path).startswith(str(cwd)):
            print(f"Error: Target path must be within the current working directory: {cwd}")
            return 1

    if not target_path.exists():
        # If target doesn't exist, just save normally
        if extractor.extracted_questions:
            extractor.save_results(str(target_path))
        else:
            # Write text content directly
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(text_to_append)
    else:
        # Append before summary using streaming to avoid reading full file
        import tempfile
        import shutil

        summary_markers = ["SUMMARY", "CUMULATIVE SUMMARY"]
        inserted = False

        # Resolve symlinks to ensure we modify the actual file
        target_path = os.path.realpath(target_path)

        # Create temp file
        target_dir = os.path.dirname(target_path)
        # Use mkstemp to create a unique temp file in the same directory (for atomic move)
        fd, temp_path = tempfile.mkstemp(dir=target_dir, text=True)

        # Copy permissions from target file to temp file
        try:
            shutil.copymode(target_path, temp_path)
        except OSError:
            pass  # Ignore if permissions cannot be copied

        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as temp_file:
                with open(target_path, 'r', encoding='utf-8') as source_file:
                    buffer_lines = []

                    for line in source_file:
                        if inserted:
                            temp_file.write(line)
                            continue

                        stripped = line.strip()
                        is_summary = stripped in summary_markers

                        if is_summary:
                            # Check for separator line in buffer
                            separator = None
                            if buffer_lines and set(buffer_lines[-1].strip()) == {'='} and len(buffer_lines[-1].strip()) > 3:
                                separator = buffer_lines.pop()

                            # Flush remaining buffer
                            for buf_line in buffer_lines:
                                temp_file.write(buf_line)
                            buffer_lines = []

                            # Insert new content
                            # Ensure surrounding newlines for clean formatting
                            if not text_to_append.startswith('\n'):
                                temp_file.write('\n')
                            temp_file.write(text_to_append)
                            if not text_to_append.endswith('\n'):
                                temp_file.write('\n')

                            # Write separator if it existed
                            if separator:
                                temp_file.write(separator)

                            # Write summary line
                            temp_file.write(line)
                            inserted = True
                        else:
                            buffer_lines.append(line)
                            # Keep a small buffer context
                            if len(buffer_lines) > 2:
                                temp_file.write(buffer_lines.pop(0))

                    # Flush remaining buffer at EOF
                    for buf_line in buffer_lines:
                        temp_file.write(buf_line)

                    if not inserted:
                        # Append at end if no summary found
                        if not text_to_append.startswith('\n'):
                            temp_file.write('\n')
                        temp_file.write(text_to_append)
                        if not text_to_append.endswith('\n'):
                            temp_file.write('\n')

            # Replace original file atomically
            shutil.move(temp_path, target_path)

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    # Update summary counts
    if update_summary:
        if not args.quiet:
            print("Updating summary counts...")
        update_summary.update_file_summary(str(target_path))

    if not args.quiet:
        print(f"✓ Appended results to {args.target}")

    return 0

def main():
    """Command line interface for the question extractor."""
    parser = argparse.ArgumentParser(
        description="ICSE Class 10 Math Question Extractor Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extractor.py --list-topics
  python extractor.py --list-units
  python extractor.py --check
  python extractor.py --generate-prompt
  python extractor.py --pdf "ICSE 2024.pdf" --prepare-images ./images
  python extractor.py --batch-manifest ./images --source "ICSE 2024"
        """
    )
    
    parser.add_argument("--list-topics", action="store_true", help="List all available topics and their status")
    parser.add_argument("--list-units", action="store_true", help="List all units in the syllabus")
    parser.add_argument("--check", action="store_true", help="Check dependencies and configuration")
    parser.add_argument("--generate-prompt", action="store_true", help="Generate extraction prompt for enabled topics")
    parser.add_argument("--topics", type=str, help="Comma-separated list of topics to use (overrides config)")
    parser.add_argument("--pdf", type=str, help="Path to PDF file to process")
    parser.add_argument("--prepare-images", type=str, help="Directory to save PDF page images")
    parser.add_argument("--batch-manifest", type=str, help="Generate batch extraction manifest for images directory")
    parser.add_argument("--source", type=str, default="", help="Source paper name for batch extraction")
    parser.add_argument("--recursive", action="store_true", help="Recursively search for images in subdirectories")
    parser.add_argument("--profile", type=str, default="class_10", help="Profile to use (default: class_10). Available: class_10, class_8")
    parser.add_argument("--enable-topic", type=str, help="Enable a topic in configuration")
    parser.add_argument("--disable-topic", type=str, help="Disable a topic in configuration")
    parser.add_argument("--syllabus-info", action="store_true", help="Show syllabus information")
    parser.add_argument("--append-results", type=str, help="File containing new questions (JSON or text) to append")
    parser.add_argument("--target", type=str, help="Target question bank file to append to")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output (useful for agent execution)")
    
    args = parser.parse_args()
    
    # Initialize extractor
    try:
        extractor = QuestionExtractor(profile=args.profile)
    except FileNotFoundError as e:
        if not args.quiet:
            print(f"Error: {e}")
        return 1
    
    # Handle commands via helpers
    if args.syllabus_info:
        return _handle_syllabus_info(extractor)
    
    if args.list_units:
        return _handle_list_units(extractor)
    
    if args.list_topics:
        return _handle_list_topics(extractor)
    
    if args.check:
        return _handle_check(extractor)
    
    if args.enable_topic or args.disable_topic:
        return _handle_topic_management(args, extractor)
    
    if args.generate_prompt:
        return _handle_prompt_generation(args, extractor)
    
    if args.batch_manifest:
        return _handle_batch_manifest(args, extractor)
    
    if args.pdf and args.prepare_images:
        return _handle_pdf_processing(args, extractor)
    
    if args.append_results and args.target:
        return _handle_append_results(args, extractor)
    
    # Default: show help
    parser.print_help()
    return 0



if __name__ == "__main__":
    exit(main())
