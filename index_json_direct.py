#!/usr/bin/env python3
"""
Simple Direct Indexing: Load all JSON files and index them to ChromaDB
Skips any files with errors and continues
"""
import sys
import os
import json
import time
from pathlib import Path
sys.path.insert(0, '.')

from src.retrieval.indexer import LegalIndexer
from src.schema import Act

def main():
    print("=" * 80)
    print("DIRECT INDEXING: Loading 366 JSON files into ChromaDB")
    print("=" * 80)
    
    processed_dir = Path("data/processed")
    json_files = list(processed_dir.glob("*.json"))
    
    print(f"\n📊 Found {len(json_files)} JSON files")
    print(f"🔄 Starting direct indexing with error skip...")
    print("=" * 80 + "\n")
    
    indexer = LegalIndexer()
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    error_files = []
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            # Load JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create Act object
            act = Act(**data)
            
            # Index it
            indexer.index_act(act)
            success_count += 1
            
            # Progress every 25 files
            if idx % 25 == 0:
                current_count = indexer.collection.count()
                print(f"Indexed: {idx}/{len(json_files)} ({idx*100//len(json_files)}%) | Chunks: {current_count:,}")
                
        except json.JSONDecodeError as e:
            error_files.append(f"{json_file.name} (JSON error)")
            error_count += 1
        except Exception as e:
            error_msg = str(e)[:80]
            error_files.append(f"{json_file.name} ({error_msg})")
            error_count += 1
    
    elapsed = time.time() - start_time
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ INDEXING COMPLETE!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   Acts successfully indexed: {success_count}/{len(json_files)}")
    print(f"   Acts with errors: {error_count}")
    print(f"   Total chunks in ChromaDB: {final_count:,}")
    if success_count > 0:
        print(f"   Average chunks per Act: {final_count//success_count}")
    print(f"\n⏱️  Time: {elapsed:.1f} seconds")
    
    if error_files and len(error_files) <= 20:
        print(f"\n⚠️  Error files ({len(error_files)}):")
        for ef in error_files[:20]:
            print(f"   - {ef}")
    
    print("\n" + "=" * 80)
    print("🎯 SYSTEM READY! Test with: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
