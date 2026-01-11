#!/usr/bin/env python3
"""
Investigate PDF structure to understand why parsing fails
"""
import sys
import os
import fitz  # PyMuPDF
sys.path.insert(0, '.')

def main():
    raw_dir = "data/raw"
    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith('.pdf')][:3]
    
    print("="*80)
    print("PDF INVESTIGATION")
    print("="*80)
    
    for pdf_file in pdf_files:
        filepath = os.path.join(raw_dir, pdf_file)
        print(f"\n📄 File: {pdf_file[:60]}")
        
        try:
            doc = fitz.open(filepath)
            print(f"   Pages: {len(doc)}")
            
            # Check first page
            if len(doc) > 0:
                page = doc[0]
                text = page.get_text()
                
                print(f"   Text length: {len(text)} characters")
                print(f"   First 200 chars:")
                print("   " + "-"*70)
                print("   " + text[:200].replace('\n', '\n   '))
                print("   " + "-"*70)
                
                # Check if it's an image-based PDF
                images = page.get_images()
                print(f"   Images on page 1: {len(images)}")
                
                if len(text.strip()) < 50 and len(images) > 0:
                    print("   ⚠️  LIKELY SCANNED PDF (image-based, little text)")
                elif len(text.strip()) > 0:
                    print("   ✓ Text-based PDF")
                else:
                    print("   ❌ No extractable text")
            
            doc.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
