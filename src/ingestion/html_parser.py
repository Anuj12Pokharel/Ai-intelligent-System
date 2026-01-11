"""
HTML Parser for Nepali Legal Documents
Handles HTML files downloaded as fallbacks when PDFs aren't available
"""
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from src.schema import Act, Part, Chapter, Section, SubSection, Clause

class NepaliHTMLParser:
    """
    Parser for HTML legal documents from Nepal Law Commission
    """
    
    # Nepali number mapping
    NEPALI_TO_ENGLISH = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    def __init__(self, filepath: str, source_url: str = ""):
        self.filepath = filepath
        self.source_url = source_url
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Regex patterns
        self.part_pattern = re.compile(r'भाग[\s-]*[\u0966-\u096F0-9]+')
        self.chapter_pattern = re.compile(r'परिच्छेद[\s-]*[\u0966-\u096F0-9]+')
        self.section_pattern = re.compile(r'दफा[\s-]*[\u0966-\u096F0-9]+')
        self.clause_pattern = re.compile(r'^\s*[\(（]?([०-९0-9]+|[क-ज्ञa-z])[\)）]?\s*[:।\.]?\s*')

    def nepali_to_english_num(self, text: str) -> str:
        """Convert Nepali numerals to English"""
        for nep, eng in self.NEPALI_TO_ENGLISH.items():
            text = text.replace(nep, eng)
        return text

    def extract_number(self, text: str) -> str:
        """Extract and normalize number from text"""
        match = re.search(r'[\u0966-\u096F0-9]+', text)
        if match:
            return self.nepali_to_english_num(match.group())
        return ""

    def extract_text_from_html(self) -> List[str]:
        """
        Extract clean text lines from HTML, handling Nepal Law Commission specific structure.
        """
        # Remove script, style, nav elements
        for element in self.soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Try to find main content area - Nepal Law Commission specific selectors
        main_content = (
            self.soup.find('div', class_='details__desc') or  # Primary content area
            self.soup.find('div', class_='detail__page-desc') or
            self.soup.find('div', class_='detail__page-inner-content') or
            self.soup.find('article') or 
            self.soup.find('main') or 
            self.soup.find('div', class_='content') or
            self.soup.body
        )
        
        if not main_content:
            return []
        
        lines = []
        
        # If details__desc is empty (flipbook case), try to extract from related cards
        if main_content.name == 'div' and not main_content.get_text(strip=True):
            # Extract metadata from the page title
            title_elem = self.soup.find('title')
            if title_elem:
                lines.append(title_elem.get_text(strip=True))
            
            # Look for any visible text content in news/related sections
            for elem in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'p']):
                text = elem.get_text(strip=True)
                if text and len(text) > 10:  # Filter tiny text
                    lines.append(text)
        else:
            # Extract text, preserving structure
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'div', 'li']):
                text = element.get_text(strip=True)
                if text:
                    lines.append(text)
        
        return lines

    def parse(self) -> Act:
        """Parse HTML into structured Act object"""
        lines = self.extract_text_from_html()
        
        act = Act(
            title=self._find_title(lines),
            source_url=self.source_url or "local_file",
            act_year=self._extract_year(lines),
            parts=[],
            chapters=[]
        )

        current_part: Optional[Part] = None
        current_chapter: Optional[Chapter] = None
        current_section: Optional[Section] = None
        content_buffer = []

        for i, line in enumerate(lines):
            # Check for Part
            if self.part_pattern.match(line):
                self._flush_section(current_section, current_chapter, content_buffer)
                self._flush_chapter(current_chapter, current_part, act)
                self._flush_part(current_part, act)
                
                current_part = Part(
                    part_number=self.extract_number(line),
                    title=self._get_title_after(lines, i),
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
                    title=self._get_title_after(lines, i),
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
                    title=self._get_title_after(lines, i),
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

    def _get_title_after(self, lines: List[str], index: int) -> str:
        """Get the title line following a structural marker"""
        if index + 1 < len(lines):
            next_line = lines[index + 1]
            # Title shouldn't be another structural marker
            if not any(pattern.match(next_line) for pattern in 
                      [self.part_pattern, self.chapter_pattern, self.section_pattern]):
                return next_line
        return ""

    def _find_title(self, lines: List[str]) -> str:
        """Extract Act title from first few lines"""
        if len(lines) >= 2:
            return ' '.join(lines[:2])
        elif lines:
            return lines[0]
        return "Unknown Act"
    
    def _extract_year(self, lines: List[str]) -> Optional[str]:
        """Extract year from title"""
        for line in lines[:5]:
            match = re.search(r'[\u0966-\u096F]{4}|[12][09]\d{2}', line)
            if match:
                return self.nepali_to_english_num(match.group())
        return None
