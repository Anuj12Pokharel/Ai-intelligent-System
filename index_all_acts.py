#!/usr/bin/env python3
"""
Complete Indexing: Process ALL 369 Acts from raw files to ChromaDB
Now that the database is fixed, this will work!
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
    print("COMPLETE INDEXING: Processing ALL 369 Acts")
    print("=" * 80)
    
    raw_dir = Path("data/raw")
    
    # Get ALL files
    pdf_files = list(raw_dir.glob("*.pdf"))
    html_files = list(raw_dir.glob("*.html")) + list(raw_dir.glob("*.htm"))
    all_files = pdf_files + html_files
    
    print(f"\n📊 Total files to process: {len(all_files)}")
    print(f"   PDFs: {len(pdf_files)}")
    print(f"   HTML: {len(html_files)}")
    print(f"\n🔄 Starting complete indexing...")
    print(f"   ⏱️  Estimated time: {len(all_files) * 1.5 / 60:.0f} minutes")
    print("=" * 80 + "\n")
    
    indexer = LegalIndexer()
    
    start_time = time.time()
    success = 0
    errors = 0
    error_files = []
    
    for idx, file_path in enumerate(all_files, 1):
        try:
            # Progress update
            if idx % 10 == 0 or idx == 1:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                remaining = (len(all_files) - idx) / rate if rate > 0 else 0
                current_count = indexer.collection.count()
                print(f"[{idx}/{len(all_files)}] {idx*100//len(all_files)}% | "
                      f"Chunks: {current_count:,} | "
                      f"ETA: {remaining/60:.0f}m")
            
            # Parse
            if file_path.suffix.lower() == '.pdf':
                parser = NepaliLegalParser(str(file_path))
                act = parser.parse()
            else:
                parser = NepaliHTMLParser(str(file_path))
                act = parser.parse()
            
            # Index
            indexer.index_act(act)
            success += 1
            
        except Exception as e:
            error_msg = str(e)[:80]
            error_files.append(f"{file_path.name}: {error_msg}")
            errors += 1
            continue
    
    elapsed = time.time() - start_time
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE INDEXING FINISHED!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   Acts successfully processed: {success}/{len(all_files)}")
    print(f"   Acts with errors: {errors}")
    print(f"   Success rate: {success*100//len(all_files)}%")
    print(f"\n💾 Database Status:")
    print(f"   Total chunks indexed: {final_count:,}")
    if success > 0:
        print(f"   Average chunks per Act: {final_count//success}")
    print(f"\n⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"   Processing rate: {len(all_files)/elapsed*60:.1f} Acts/hour")
    
    if error_files and len(error_files) <= 20:
        print(f"\n⚠️  Error files ({len(error_files)}):")
        for ef in error_files[:20]:
            print(f"   - {ef}")
    
    print("\n" + "=" * 80)
    print("🎯 SYSTEM READY! Test with: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
