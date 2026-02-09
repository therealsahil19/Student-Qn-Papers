import os
from pathlib import Path
from typing import List, Dict, Optional
from question_extractor.topic_manager import TopicManager

class PromptGenerator:
    """Generates prompts for AI-powered question extraction."""

    def __init__(self, topic_manager: TopicManager):
        self.topic_manager = topic_manager

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
        
        board = self.topic_manager.get_syllabus_info().get('board', 'ICSE')
        class_num = self.topic_manager.get_syllabus_info().get('class', '10')
        
        prompt = f"""
# {board} Class {class_num} Mathematics Question Extraction{page_context}

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
        image_provider_func, # Function to get all image paths
        topics: List[str] = None,
        source_paper: str = "",
        recursive: bool = False
    ) -> Dict:
        """
        Generate a manifest for batch extraction of ALL pages.
        
        Args:
            images_dir: Directory containing page images
            image_provider_func: Function to get image paths sorted (QuestionExtractor.get_all_image_paths)
            topics: Topics to extract (None = use enabled)
            source_paper: Name of the source paper
            recursive: If True, search subdirectories for images
            
        Returns:
            Manifest dictionary with extraction plan
        """
        if recursive:
            image_paths = []
            # Recursive scan
            def scan_dir(path):
                try:
                    with os.scandir(path) as it:
                        for entry in it:
                            if entry.is_dir():
                                scan_dir(entry.path)
                            elif entry.is_file() and entry.name.lower().endswith('.png'):
                                image_paths.append(entry.path)
                except OSError:
                    pass 

            scan_dir(str(images_dir))

            def get_page_num(path_str):
                try:
                    name = os.path.basename(path_str)
                    return int(name.rpartition('_')[2][:-4])
                except:
                    return 0
            
            image_paths.sort(key=get_page_num)
            image_paths = [str(Path(p).absolute()) for p in image_paths]
        else:
            image_paths = image_provider_func(images_dir)
        
        if topics is None:
            topics = list(self.topic_manager.get_enabled_topics().keys())
        
        # Generate the instruction prompt once for the whole batch
        extraction_prompt = self.generate_extraction_prompt(
            topics=topics,
            is_batch_mode=True,
            include_examples=True
        )

        manifest = {
            "source_paper": source_paper,
            "images_directory": str(images_dir),
            "total_pages": len(image_paths),
            "target_topics": topics,
            "extraction_prompt": extraction_prompt,
            "pages": []
        }
        
        for idx, img_path in enumerate(image_paths, 1):
            page_source = source_paper
            if recursive:
                page_source = Path(img_path).parent.name

            page_info = {
                "page_number": idx,
                "image_path": img_path,
                "source_paper": page_source,
                "status": "pending",
                "questions_extracted": 0
            }
            manifest["pages"].append(page_info)
        
        return manifest
