#!/usr/bin/env python3
"""
Quick Fix: Process Acts directly from raw files to ChromaDB
Bypasses JSON serialization - processes and indexes in memory
"""
import sys
import os
import time
from pathlib import Path
sys.path.insert(0, '.')

from src.ingestion.parser import NepaliLegalParser
from src.ingestion.html_parser import NepaliHTMLParser
from src.retrieval.indexer import LegalIndexer

def main():
    print("=" * 80)
    print("QUICK FIX: Direct Raw-to-ChromaDB Processing")
    print("=" * 80)
    
    raw_dir = Path("data/raw")
    
    # Get first 30 files for proof of concept
    pdf_files = list(raw_dir.glob("*.pdf"))[:20]
    html_files = list(raw_dir.glob("*.html"))[:10]
    all_files = pdf_files + html_files
    
    print(f"\n📊 Processing {len(all_files)} files:")
    print(f"   PDFs: {len(pdf_files)}")
    print(f"   HTML: {len(html_files)}")
    print(f"\n🔄 Parsing and indexing directly (no JSON)...")
    print("=" * 80 + "\n")
    
    indexer = LegalIndexer()
    
    start_time = time.time()
    success = 0
    errors = 0
    
    for idx, file_path in enumerate(all_files, 1):
        try:
            print(f"[{idx}/{len(all_files)}] Processing: {file_path.name[:60]}...")
            
            # Parse directly
            if file_path.suffix.lower() == '.pdf':
                parser = NepaliLegalParser(str(file_path))
                act = parser.parse()
            else:
                parser = NepaliHTMLParser(str(file_path))
                act = parser.parse()
            
            # Index immediately (no JSON serialization)
            indexer.index_act(act)
            success += 1
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
            errors += 1
            continue
    
    elapsed = time.time() - start_time
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ QUICK FIX COMPLETE!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   Acts processed: {success}/{len(all_files)}")
    print(f"   Errors: {errors}")
    print(f"   Total chunks indexed: {final_count:,}")
    if success > 0:
        print(f"   Average chunks per Act: {final_count//success}")
    print(f"\n⏱️  Time: {elapsed:.1f} seconds")
    
    print("\n" + "=" * 80)
    print("🎯 SYSTEM READY! Test with: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
