#!/usr/bin/env python3
"""
Check what's in the first 20 lines of a sample PDF
"""
import sys
import os
import fitz
sys.path.insert(0, '.')

raw_dir = "data/raw"
pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')]

if pdf_files:
    filepath = os.path.join(raw_dir, pdf_files[0])
    print(f"Checking: {pdf_files[0][:60]}\n")
    
    doc = fitz.open(filepath)
    page = doc[0]
    text = page.get_text("text")
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    print("First 20 lines:")
    print("="*60)
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2}. {line[:70]}")
    print("="*60)
    
    doc.close()
