#!/usr/bin/env python3
"""
Deep investigation: Check actual PDF content against parser patterns
"""
import sys
import os
import re
import fitz
sys.path.insert(0, '.')

from src.ingestion.parser import NepaliLegalParser

def main():
    raw_dir = "data/raw"
    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')][:1]
    
    if not pdf_files:
        print("No PDF files found")
        return
    
    filepath = os.path.join(raw_dir, pdf_files[0])
    print(f"Analyzing: {pdf_files[0][:60]}\n")
    
    # Get text
    doc = fitz.open(filepath)
    all_text = []
    for page in doc:
        text = page.get_text("text")
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        all_text.extend(lines)
    doc.close()
    
    # Check patterns from parser
    parser = NepaliLegalParser(filepath)
    
    print("="*70)
    print("PATTERN TESTING")
    print("="*70)
    
    # Test patterns
    section_pattern = re.compile(r'दफा\s*[०-९०-९०-९०-९\d]+')
    chapter_pattern = re.compile(r'परिच्छेद[–\-\s]*[०-९\d]+')
    part_pattern = re.compile(r'भाग[–\-\s]*[०-९\d]+')
    
    print(f"\nSection pattern: {section_pattern.pattern}")
    print(f"Chapter pattern: {chapter_pattern.pattern}")
    print(f"Part pattern: {part_pattern.pattern}\n")
    
    section_matches = []
    chapter_matches = []
    part_matches = []
    
    for i, line in enumerate(all_text[:200], 1):  # Check first 200 lines
        if section_pattern.search(line):
            section_matches.append((i, line[:60]))
        if chapter_pattern.search(line):
            chapter_matches.append((i, line[:60]))
        if part_pattern.search(line):
            part_matches.append((i, line[:60]))
    
    print(f"Parts found: {len(part_matches)}")
    for line_num, text in part_matches[:5]:
        print(f"  Line {line_num}: {text}")
    
    print(f"\nChapters found: {len(chapter_matches)}")
    for line_num, text in chapter_matches[:5]:
        print(f"  Line {line_num}: {text}")
    
    print(f"\nSections (दफा) found: {len(section_matches)}")
    for line_num, text in section_matches[:10]:
        print(f"  Line {line_num}: {text}")
    
    # Show some sample lines that might be sections
    print(f"\n{'='*70}")
    print("SAMPLE LINES (looking for section patterns)")
    print("="*70)
    for i, line in enumerate(all_text[20:60], 21):
        marker = ""
        if section_pattern.search(line):
            marker = " ← SECTION"
        elif chapter_pattern.search(line):
            marker = " ← CHAPTER"
        print(f"{i:3}. {line[:65]}{marker}")

if __name__ == "__main__":
    main()
