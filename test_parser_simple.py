#!/usr/bin/env python3
"""
Simple test: Parse ONE PDF and show what we get
"""
import sys
sys.path.insert(0, '.')

from src.ingestion.parser import NepaliLegalParser
import os

raw_dir = "data/raw"
pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')]

if pdf_files:
    filepath = os.path.join(raw_dir, pdf_files[0])
    print(f"Parsing: {pdf_files[0][:50]}\n")
    
    parser = NepaliLegalParser(filepath)
    act = parser.parse()
    
    print(f"Title: {act.title[:80]}")
    print(f"Year: {act.act_year}")
    print(f"Parts: {len(act.parts)}")
    print(f"Chapters (direct): {len(act.chapters)}")
    
    if act.parts:
        for i, part in enumerate(act.parts[:3]):
            print(f"\nPart {i+1}: {part.part_number} - {part.title[:40] if part.title else 'No title'}")
            print(f"  Chapters in part: {len(part.chapters)}")
            
            if part.chapters:
                for j, chap in enumerate(part.chapters[:2]):
                    print(f"    Chapter {j+1}: {chap.chapter_number} - Sections: {len(chap.sections)}")
    
    if act.chapters:
        for i, chap in enumerate(act.chapters[:3]):
            print(f"\nChapter {i+1}: {chap.chapter_number} - Sections: {len(chap.sections)}")
    
    # Check if we found ANY structure
    total_items = len(act.parts) + len(act.chapters)
    if total_items == 0:
        print("\n⚠️  NO STRUCTURE FOUND - Parser not detecting parts/chapters")
        print("\nShowing first 10 text lines from PDF:")
        parser.extract_text()
        for i, line in enumerate(parser.text_lines[:10], 1):
            print(f"{i}. {line[:70]}")
else:
    print("No PDF files found")
