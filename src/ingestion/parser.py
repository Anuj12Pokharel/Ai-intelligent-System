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

        # FALLBACK: If no structure found, create default structure from content
        if len(act.parts) == 0 and len(act.chapters) == 0:
            # Try to find Parts and Chapters first
            current_part = None
            current_chapter = None
            current_section = None
            content_buffer = []
            
            for i, line in enumerate(self.text_lines):
                # Check for Part (भाग) - very flexible
                if 'भाग' in line and any(c.isdigit() or '\u0966' <= c <= '\u096F' for c in line):
                    # Flush previous
                    if current_section and content_buffer:
                        current_section.content = ' '.join(content_buffer)
                        clauses = self.detect_clauses(current_section.content)
                        if clauses:
                            current_section.clauses = clauses
                        if current_chapter:
                            current_chapter.sections.append(current_section)
                    
                    if current_chapter and current_part:
                        current_part.chapters.append(current_chapter)
                    
                    if current_part:
                        act.parts.append(current_part)
                    
                    # Start new Part
                    part_num = self.extract_number(line)
                    current_part = Part(
                        part_number=part_num if part_num else str(len(act.parts) + 1),
                        title=line,
                        chapters=[]
                    )
                    current_chapter = None
                    current_section = None
                    content_buffer = []
                    continue
                
                # Check for Chapter (परिच्छेद) - very flexible
                if 'परिच्छेद' in line and any(c.isdigit() or '\u0966' <= c <= '\u096F' for c in line):
                    # Flush previous section
                    if current_section and content_buffer:
                        current_section.content = ' '.join(content_buffer)
                        clauses = self.detect_clauses(current_section.content)
                        if clauses:
                            current_section.clauses = clauses
                        if current_chapter:
                            current_chapter.sections.append(current_section)
                    
                    if current_chapter and current_part:
                        current_part.chapters.append(current_chapter)
                    
                    # Start new Chapter
                    chap_num = self.extract_number(line)
                    current_chapter = Chapter(
                        chapter_number=chap_num if chap_num else str(len(current_part.chapters) + 1 if current_part else 1),
                        title=line,
                        sections=[]
                    )
                    current_section = None
                    content_buffer = []
                    continue
                
                # Check for Section (दफा/धारा) - very flexible
                if ('दफा' in line or 'धारा' in line) and any(c.isdigit() or '\u0966' <= c <= '\u096F' for c in line):
                    # Flush previous section
                    if current_section and content_buffer:
                        current_section.content = ' '.join(content_buffer)
                        clauses = self.detect_clauses(current_section.content)
                        if clauses:
                            current_section.clauses = clauses
                        
                        # Add to current chapter or create default
                        if not current_chapter:
                            current_chapter = Chapter(
                                chapter_number="1",
                                title="सामान्य (General)",
                                sections=[]
                            )
                        current_chapter.sections.append(current_section)
                    
                    # Start new section
                    section_num = self.extract_number(line)
                    current_section = Section(
                        section_number=section_num if section_num else "1",
                        title=line if len(line) < 100 else "",
                        content="",
                        sub_sections=[]
                    )
                    content_buffer = []
                elif current_section:
                    # Accumulate content for current section
                    content_buffer.append(line)
            
            # Flush remaining structures
            if current_section and content_buffer:
                current_section.content = ' '.join(content_buffer)
                clauses = self.detect_clauses(current_section.content)
                if clauses:
                    current_section.clauses = clauses
                if not current_chapter:
                    current_chapter = Chapter(
                        chapter_number="1",
                        title="सामान्य (General)",
                        sections=[]
                    )
                current_chapter.sections.append(current_section)
            
            # Flush chapter into part or act
            if current_chapter:
                if current_part:
                    current_part.chapters.append(current_chapter)
                else:
                    # No parts found, add chapter directly to act
                    act.chapters.append(current_chapter)
            
            # Flush part
            if current_part:
                act.parts.append(current_part)

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
        """Extract Act title from lines containing 'ऐन'"""
        # Look for line containing 'ऐन' (Act) keyword - this is the title
        for i, line in enumerate(self.text_lines[:50]):  # Check first 50 lines
            if 'ऐन' in line:
                # Found Act title - may span multiple lines
                title_parts = [line]
                
                # Check if previous line is part of title (no section/chapter markers)
                if i > 0 and not self.section_pattern.match(self.text_lines[i-1]):
                    prev_line = self.text_lines[i-1]
                    # Skip if it looks like header/footer
                    if not ('www.' in prev_line or 'http' in prev_line or len(prev_line) < 5):
                        title_parts.insert(0, prev_line)
                
                # Check if next line continues the title
                if i+1 < len(self.text_lines) and not self.section_pattern.match(self.text_lines[i+1]):
                    next_line = self.text_lines[i+1]
                    if not ('www.' in next_line or 'http' in next_line) and len(next_line) > 3:
                        # Only add if it doesn't look like a new section
                        if not self.chapter_pattern.match(next_line) and not self.part_pattern.match(next_line):
                            title_parts.append(next_line)
                
                return ' '.join(title_parts).strip()
        
        # Fallback: look for common patterns
        for line in self.text_lines[:20]:
            # Skip obvious headers/footers
            if 'www.' in line or 'http' in line or len(line) < 5:
                continue
            # Skip page numbers
            if line.isdigit() or (len(line) < 4 and any(c.isdigit() for c in line)):
                continue
            return line
        
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
