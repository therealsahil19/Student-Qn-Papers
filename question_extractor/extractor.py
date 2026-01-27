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
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import glob

# Import local modules
try:
    from pdf_processor import PDFProcessor, PDFPage
except ImportError:
    PDFProcessor = None
    PDFPage = None


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


class TopicManager:
    """Manages topic configuration and filtering for ICSE syllabus."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize with topic configuration.
        
        Args:
            config_path: Path to topics_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent / "topics_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Topic configuration not found: {self.config_path}\n"
                "Please ensure topics_config.json exists in the question_extractor folder."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_syllabus_info(self) -> dict:
        """Get syllabus metadata."""
        return self.config.get("syllabus_info", {})
    
    def get_all_units(self) -> Dict[str, dict]:
        """Get all units in the syllabus."""
        return self.config.get("units", {})
    
    def get_enabled_topics(self) -> Dict[str, dict]:
        """Get all topics that are enabled across all units."""
        enabled = {}
        units = self.config.get("units", {})
        
        for unit_key, unit_data in units.items():
            if not unit_data.get("enabled", True):
                continue
            
            topics = unit_data.get("topics", {})
            for topic_key, topic_data in topics.items():
                if topic_data.get("enabled", True):
                    # Add unit info to topic
                    topic_with_unit = topic_data.copy()
                    topic_with_unit["unit"] = unit_data.get("unit_name", unit_key)
                    topic_with_unit["unit_key"] = unit_key
                    enabled[topic_key] = topic_with_unit
        
        return enabled
    
    def get_all_topics(self) -> Dict[str, dict]:
        """Get all topics regardless of enabled status."""
        all_topics = {}
        units = self.config.get("units", {})
        
        for unit_key, unit_data in units.items():
            topics = unit_data.get("topics", {})
            for topic_key, topic_data in topics.items():
                topic_with_unit = topic_data.copy()
                topic_with_unit["unit"] = unit_data.get("unit_name", unit_key)
                topic_with_unit["unit_key"] = unit_key
                all_topics[topic_key] = topic_with_unit
        
        return all_topics
    
    def get_topic_names(self, enabled_only: bool = True) -> List[str]:
        """Get list of topic names."""
        if enabled_only:
            return list(self.get_enabled_topics().keys())
        return list(self.get_all_topics().keys())
    
    def get_topic_keywords(self, topic_name: str) -> List[str]:
        """Get keywords for a specific topic."""
        topics = self.get_all_topics()
        if topic_name in topics:
            return topics[topic_name].get("keywords", [])
        return []
    
    def get_topic_by_name(self, topic_name: str) -> Optional[dict]:
        """Get full topic data by name."""
        topics = self.get_all_topics()
        return topics.get(topic_name)
    
    def enable_topic(self, topic_name: str) -> bool:
        """Enable a topic in the configuration."""
        units = self.config.get("units", {})
        for unit_data in units.values():
            topics = unit_data.get("topics", {})
            if topic_name in topics:
                topics[topic_name]["enabled"] = True
                return True
        return False
    
    def disable_topic(self, topic_name: str) -> bool:
        """Disable a topic in the configuration."""
        units = self.config.get("units", {})
        for unit_data in units.values():
            topics = unit_data.get("topics", {})
            if topic_name in topics:
                topics[topic_name]["enabled"] = False
                return True
        return False
    
    def save_config(self):
        """Save current configuration back to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_extraction_settings(self) -> dict:
        """Get extraction settings from config."""
        return self.config.get("extraction_settings", {
            "include_marks": True,
            "include_question_number": True,
            "include_sub_parts": True,
            "output_format": "txt"
        })


class QuestionExtractor:
    """
    Main class for extracting questions from ICSE Math papers.
    
    This framework prepares PDFs for visual analysis and provides
    structured prompts for AI-powered question extraction.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the question extractor.
        
        Args:
            config_path: Path to topics_config.json
        """
        self.topic_manager = TopicManager(config_path)
        self.pdf_processor = PDFProcessor() if PDFProcessor else None
        self.extracted_questions: List[ExtractedQuestion] = []
        self._existing_signatures = set()  # Set of (question_number, source_paper) for fast lookup
        self.processed_pages: Dict[str, List[int]] = {}  # Track processed pages per paper
    
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
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            List of PDFPage objects with image data
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
        
        Args:
            images_dir: Directory containing page images
            
        Returns:
            List of absolute paths to images, sorted by page number
        """
        images_dir = Path(images_dir)
        if not images_dir.exists():
            return []
        
        # Find all PNG images
        image_files = list(images_dir.glob("*.png"))
        
        # Sort by page number (extract number from filename like page_001.png)
        def get_page_num(path):
            name = path.stem  # e.g., "page_001"
            try:
                return int(name.split("_")[-1])
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
        """
        Generate a prompt for AI-powered question extraction.
        
        This prompt can be used with vision-capable AI models like
        Claude or Gemini to extract questions from PDF images.
        
        Args:
            topics: List of topic names to extract (None = use enabled topics)
            include_examples: Whether to include example output format
            page_number: Optional page number for context
            is_batch_mode: If True, generates a more thorough prompt for batch processing
            
        Returns:
            Formatted prompt string
        """
        if topics is None:
            enabled = self.topic_manager.get_enabled_topics()
            topics = list(enabled.keys())
        
        # Build comprehensive topic descriptions with ALL keywords
        topic_descriptions = []
        all_topics = self.topic_manager.get_all_topics()
        for topic_name in topics:
            if topic_name in all_topics:
                topic_data = all_topics[topic_name]
                # Include ALL keywords for comprehensive matching
                keywords = ", ".join(topic_data.get("keywords", []))
                subtopics = topic_data.get("subtopics", [])
                subtopics_str = ", ".join(subtopics) if subtopics else "N/A"
                unit = topic_data.get("unit", "Unknown")
                formulas = topic_data.get("formulas", [])
                formulas_str = "; ".join(formulas[:5]) if formulas else ""
                edge_cases = topic_data.get("edge_cases", [])
                
                desc = f"""
### {topic_name} ({topic_data.get('full_name', topic_name)})
- **Unit**: {unit}
- **Keywords**: {keywords}
- **Subtopics**: {subtopics_str}"""
                if formulas_str:
                    desc += f"\n- **Common Formulas**: {formulas_str}"
                if edge_cases:
                    desc += f"\n- **Look for**: {', '.join(edge_cases[:3])}"
                
                topic_descriptions.append(desc)
        
        settings = self.topic_manager.get_extraction_settings()
        
        page_context = f" (Page {page_number})" if page_number else ""
        
        prompt = f"""
# ICSE Class 10 Mathematics Question Extraction{page_context}

## YOUR TASK
You MUST extract **EVERY SINGLE QUESTION** from this page that belongs to ANY of the following topics. 
Do NOT skip any question. Even if a question only partially relates to a topic, include it.

## TARGET TOPICS (Extract ALL questions matching these):
{chr(10).join(topic_descriptions)}

## EXTRACTION RULES - FOLLOW EXACTLY:

1. **SCAN THE ENTIRE PAGE** - Look at every question, sub-question, and part.

2. **QUESTION IDENTIFICATION**:
   - Section A questions (MCQs): Usually numbered 1(i), 1(ii), 1(iii), etc.
   - Section B questions (Descriptive): Usually numbered as Question 2, Question 3, etc. with parts (i), (ii), (iii) or (a), (b), (c)
   
3. **FOR EACH MATCHING QUESTION, EXTRACT**:
   - Question number (exactly as shown, e.g., "1(i)", "4(ii)(a)", "Q5(b)")
   - COMPLETE question text (include ALL given information, conditions, values)
   - Topic classification (from the list above)
   - Unit name
   - Subtopic (be specific)
   - Marks (look for [3], [4 marks], etc.)
   - Has diagram (true/false)
   - Difficulty (easy/medium/hard)

4. **COMPLETENESS CHECKLIST**:
   ✓ Did you check EVERY question on this page?
   ✓ Did you include ALL MCQs that match the topics?
   ✓ Did you include ALL descriptive questions that match?
   ✓ Did you extract sub-parts separately if they have different topics?

5. **TOPIC MATCHING GUIDE**:
   - GST: Any question mentioning tax, CGST, SGST, IGST, invoice, marked price with tax
   - Banking: Recurring deposit, interest, maturity, savings account, fixed deposit
   - Shares/Dividends: Shares, dividends, nominal value, market value, premium, discount, investment

"""
        
        if include_examples:
            prompt += """
## OUTPUT FORMAT (JSON) - One entry per question/sub-question:
```json
{
  "page_questions": [
    {
      "question_number": "1(i)",
      "question_text": "For an Intra-state sale, the CGST paid by a dealer to the Central government is ₹120. If the marked price of the article is ₹2000, the rate of GST is: (a) 6% (b) 10% (c) 12% (d) 16.67%",
      "topic": "GST",
      "unit": "Commercial Mathematics",
      "subtopic": "GST Rate Calculation",
      "marks": 1,
      "has_diagram": false,
      "difficulty": "easy"
    },
    {
      "question_number": "4(i)",
      "question_text": "Suresh has a recurring deposit account in a bank. He deposits ₹2000 per month and the bank pays interest at the rate of 8% per annum. If he gets ₹1040 as interest at the time of maturity, find in years total time for which the account was held.",
      "topic": "Banking",
      "unit": "Commercial Mathematics", 
      "subtopic": "Recurring Deposit - Time Calculation",
      "marks": 3,
      "has_diagram": false,
      "difficulty": "medium"
    }
  ],
  "extraction_notes": "Extracted 2 questions from this page matching GST and Banking topics."
}
```

## IMPORTANT REMINDERS:
- If NO questions match the topics on this page, return: {"page_questions": [], "extraction_notes": "No matching questions found on this page."}
- Extract COMPLETE question text - do not summarize or shorten
- Include ALL options for MCQs
- Include ALL parts (a, b, c) for descriptive questions
"""
        
        return prompt
    
    def generate_batch_extraction_manifest(
        self,
        images_dir: str,
        topics: List[str] = None,
        source_paper: str = ""
    ) -> Dict:
        """
        Generate a manifest for batch extraction of ALL pages.
        
        This creates a structured plan for extracting from every page,
        ensuring complete coverage.
        
        Args:
            images_dir: Directory containing page images
            topics: Topics to extract (None = use enabled)
            source_paper: Name of the source paper
            
        Returns:
            Manifest dictionary with extraction plan
        """
        image_paths = self.get_all_image_paths(images_dir)
        
        if topics is None:
            topics = list(self.topic_manager.get_enabled_topics().keys())
        
        manifest = {
            "source_paper": source_paper,
            "images_directory": str(images_dir),
            "total_pages": len(image_paths),
            "target_topics": topics,
            "pages": []
        }
        
        for idx, img_path in enumerate(image_paths, 1):
            page_info = {
                "page_number": idx,
                "image_path": img_path,
                "status": "pending",
                "questions_extracted": 0
            }
            manifest["pages"].append(page_info)
        
        return manifest
    
    def add_question(self, question: ExtractedQuestion):
        """Add an extracted question to the collection."""
        # Check for duplicates based on question number and source
        signature = (question.question_number, question.source_paper)
        if signature not in self._existing_signatures:
            self._existing_signatures.add(signature)
            self.extracted_questions.append(question)
    
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
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', json_data, re.DOTALL)
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
                source_paper=source_paper
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
        questions = [q for q in self.extracted_questions if q.source_paper == source_paper]
        
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
    
    def save_results(self, output_path: str, format: str = "txt"):
        """
        Save extracted questions to file.
        
        Args:
            output_path: Path for output file
            format: Output format (txt, json, or markdown)
        """
        output_path = Path(output_path)
        
        if format == "json":
            data = {
                "extracted_at": datetime.now().isoformat(),
                "total_questions": len(self.extracted_questions),
                "summary": self.get_questions_summary(),
                "processed_pages": self.processed_pages,
                "questions": [asdict(q) for q in self.extracted_questions]
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == "txt":
            lines = [
                "=" * 70,
                "ICSE CLASS 10 MATHEMATICS - EXTRACTED QUESTION BANK",
                "=" * 70,
                f"Extracted at: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"Total questions: {len(self.extracted_questions)}",
                "=" * 70,
                ""
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
                        if q.subtopic:
                            lines.append(f"    Subtopic: {q.subtopic}")
                        if source_str:
                            lines.append(f"    {source_str}")
                        lines.append("")
                        lines.append("    " + "-" * 40)
                        lines.append("")
            
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
        
        elif format == "markdown":
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
        
        print(f"✓ Saved {len(self.extracted_questions)} questions to {output_path}")
    
    def clear_questions(self):
        """Clear all extracted questions."""
        self.extracted_questions = []
        self._existing_signatures = set()
        self.processed_pages = {}


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
    
    parser.add_argument(
        "--list-topics", 
        action="store_true",
        help="List all available topics and their status"
    )
    parser.add_argument(
        "--list-units",
        action="store_true",
        help="List all units in the syllabus"
    )
    parser.add_argument(
        "--check",
        action="store_true", 
        help="Check dependencies and configuration"
    )
    parser.add_argument(
        "--generate-prompt",
        action="store_true",
        help="Generate extraction prompt for enabled topics"
    )
    parser.add_argument(
        "--topics",
        type=str,
        help="Comma-separated list of topics to use (overrides config)"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        help="Path to PDF file to process"
    )
    parser.add_argument(
        "--prepare-images",
        type=str,
        help="Directory to save PDF page images"
    )
    parser.add_argument(
        "--batch-manifest",
        type=str,
        help="Generate batch extraction manifest for images directory"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="",
        help="Source paper name for batch extraction"
    )
    parser.add_argument(
        "--enable-topic",
        type=str,
        help="Enable a topic in configuration"
    )
    parser.add_argument(
        "--disable-topic", 
        type=str,
        help="Disable a topic in configuration"
    )
    parser.add_argument(
        "--syllabus-info",
        action="store_true",
        help="Show syllabus information"
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    try:
        extractor = QuestionExtractor()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Handle commands
    if args.syllabus_info:
        info = extractor.topic_manager.get_syllabus_info()
        print("\n📚 ICSE Class 10 Mathematics Syllabus 2026\n")
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
    
    if args.list_units:
        print("\n📖 ICSE Class 10 Math Units\n")
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
    
    if args.list_topics:
        print("\n📚 ICSE Class 10 Math Topics\n")
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
    
    if args.check:
        print("\n🔍 Dependency Check\n")
        status = extractor.check_dependencies()
        for key, value in status.items():
            icon = "✓" if value else "✗"
            print(f"  {icon} {key}: {value}")
        print()
        return 0
    
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
    
    if args.generate_prompt:
        topics = args.topics.split(",") if args.topics else None
        prompt = extractor.generate_extraction_prompt(topics=topics, is_batch_mode=True)
        print("\n" + "=" * 60)
        print("EXTRACTION PROMPT")
        print("=" * 60)
        print(prompt)
        print("=" * 60 + "\n")
        return 0
    
    if args.batch_manifest:
        topics = args.topics.split(",") if args.topics else None
        manifest = extractor.generate_batch_extraction_manifest(
            args.batch_manifest,
            topics=topics,
            source_paper=args.source
        )
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
        print(f"✓ Manifest saved to {manifest_path}")
        return 0
    
    if args.pdf and args.prepare_images:
        print(f"\n📄 Processing: {args.pdf}")
        try:
            pages = extractor.prepare_pdf(args.pdf, args.prepare_images)
            print(f"✓ Converted {len(pages)} pages to images in {args.prepare_images}")
            for page in pages:
                print(f"  - Page {page.page_number}: {page.image_path}")
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
        return 0
    
    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(main())
