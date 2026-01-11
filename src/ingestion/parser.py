import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Optional
from src.schema import Act, Part, Chapter, Section, SubSection, Clause

class NepaliLegalParser:
    """
    Enhanced parser for Nepali legal documents with robust Unicode handling.
    Handles complex hierarchical structures: Act -> Part -> Chapter -> Section -> Subsection -> Clause
    """
    
    # Nepali number mapping for conversion
    NEPALI_TO_ENGLISH = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    def __init__(self, filepath: str, source_url: str = ""):
        self.filepath = filepath
        self.source_url = source_url
        self.doc = fitz.open(filepath)
        self.text_lines = []
        
        # Regex patterns for hierarchical elements
        # भाग (Part): भाग-१, भाग १
        self.part_pattern = re.compile(r'भाग[\s-]*[\u0966-\u096F0-9]+')
        
        # परिच्छेद (Chapter): परिच्छेद-१, परिच्छेद १
        self.chapter_pattern = re.compile(r'परिच्छेद[\s-]*[\u0966-\u096F0-9]+')
        
        # दफा (Section): दफा १, दफा-१
        self.section_pattern = re.compile(r'दफा[\s-]*[\u0966-\u096F0-9]+')
        
        # Clause patterns: (१), (क), १., क.
        self.clause_pattern = re.compile(r'^\s*[\(（]?([०-९0-9]+|[क-ज्ञa-z])[\)）]?\s*[:।\.]?\s*')
        
        # Sub-section pattern: उपदफा
        self.subsection_pattern = re.compile(r'उपदफा[\s-]*[\u0966-\u096F0-9]+')

    def nepali_to_english_num(self, text: str) -> str:
        """Convert Nepali numerals to English"""
        for nep, eng in self.NEPALI_TO_ENGLISH.items():
            text = text.replace(nep, eng)
        return text

    def extract_number(self, text: str) -> str:
        """Extract and normalize number from text"""
        # Extract Nepali or English digits
        match = re.search(r'[\u0966-\u096F0-9]+', text)
        if match:
            return self.nepali_to_english_num(match.group())
        return ""

    def extract_text(self):
        """Extract text from all pages preserving structure"""
        all_text = []
        for page_num, page in enumerate(self.doc):
            text = page.get_text("text")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            all_text.extend(lines)
        self.text_lines = all_text
        return self.text_lines

    def detect_clauses(self, content: str) -> List[Clause]:
        """Extract clauses from section content"""
        clauses = []
        lines = content.split('\n')
        current_clause = None
        
        for line in lines:
            match = self.clause_pattern.match(line)
            if match:
                # Save previous clause
                if current_clause:
                    clauses.append(current_clause)
                
                # Start new clause
                clause_id = match.group(1)
                clause_text = self.clause_pattern.sub('', line).strip()
                current_clause = Clause(
                    clause_id=self.nepali_to_english_num(clause_id),
                    content=clause_text
                )
            elif current_clause:
                # Continue previous clause
                current_clause.content += " " + line.strip()
        
        # Add last clause
        if current_clause:
            clauses.append(current_clause)
            
        return clauses

    def parse(self) -> Act:
        """Main parsing logic with hierarchical structure detection"""
        self.extract_text()
        
        act = Act(
            title=self._find_title(),
            source_url=self.source_url or "local_file",
            act_year=self._extract_year(),
            parts=[],
            chapters=[]
        )

        current_part: Optional[Part] = None
        current_chapter: Optional[Chapter] = None
        current_section: Optional[Section] = None
        content_buffer = []

        for i, line in enumerate(self.text_lines):
            # Check for Part
            if self.part_pattern.match(line):
                self._flush_section(current_section, current_chapter, content_buffer)
                self._flush_chapter(current_chapter, current_part, act)
                self._flush_part(current_part, act)
                
                current_part = Part(
                    part_number=self.extract_number(line),
                    title=self._get_title_after(i),
                    chapters=[]
                )
                current_chapter = None
                current_section = None
                content_buffer = []
                continue
            
            # Check for Chapter
            if self.chapter_pattern.match(line):
                self._flush_section(current_section, current_chapter, content_buffer)
                self._flush_chapter(current_chapter, current_part, act)
                
                current_chapter = Chapter(
                    chapter_number=self.extract_number(line),
                    title=self._get_title_after(i),
                    sections=[]
                )
                current_section = None
                content_buffer = []
                continue
            
            # Check for Section
            if self.section_pattern.match(line):
                self._flush_section(current_section, current_chapter, content_buffer)
                
                current_section = Section(
                    section_number=self.extract_number(line),
                    title=self._get_title_after(i),
                    content="",
                    sub_sections=[]
                )
                content_buffer = []
                continue
            
            # Accumulate content
            if current_section is not None:
                content_buffer.append(line)

        # Flush remaining
        self._flush_section(current_section, current_chapter, content_buffer)
        self._flush_chapter(current_chapter, current_part, act)
        self._flush_part(current_part, act)

        return act

    def _flush_section(self, section, chapter, content_buffer):
        """Add completed section to chapter"""
        if section and chapter is not None:
            section.content = '\n'.join(content_buffer)
            # Detect clauses within content
            clauses = self.detect_clauses(section.content)
            if clauses:
                section.clauses = clauses
            chapter.sections.append(section)

    def _flush_chapter(self, chapter, part, act):
        """Add completed chapter to part or act"""
        if chapter:
            if part:
                part.chapters.append(chapter)
            else:
                act.chapters.append(chapter)

    def _flush_part(self, part, act):
        """Add completed part to act"""
        if part:
            act.parts.append(part)

    def _get_title_after(self, index: int) -> str:
        """Get the title line following a structural marker"""
        if index + 1 < len(self.text_lines):
            next_line = self.text_lines[index + 1]
            # Title shouldn't be another structural marker
            if not any(pattern.match(next_line) for pattern in 
                      [self.part_pattern, self.chapter_pattern, self.section_pattern]):
                return next_line
        return ""

    def _find_title(self) -> str:
        """Extract Act title from first few lines"""
        if len(self.text_lines) >= 2:
            # Usually first 2-3 lines contain title
            return ' '.join(self.text_lines[:2])
        elif self.text_lines:
            return self.text_lines[0]
        return "Unknown Act"
    
    def _extract_year(self) -> Optional[str]:
        """Extract year from title (e.g., २०७४, 2074)"""
        for line in self.text_lines[:5]:
            # Look for 4-digit year in Nepali or English
            match = re.search(r'[\u0966-\u096F]{4}|[12][09]\d{2}', line)
            if match:
                return self.nepali_to_english_num(match.group())
        return None


if __name__ == "__main__":
    # Test with sample file
    # parser = NepaliLegalParser("data/raw/sample.pdf", "https://lawcommission.gov.np/...")
    # act = parser.parse()
    # print(act.model_dump_json(indent=2))
    pass
