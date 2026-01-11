#!/usr/bin/env python3
"""
Complete Rebuild: Index all 368 processed Acts into fresh ChromaDB
"""
import sys
import os
import json
import time
sys.path.insert(0, '.')

from src.retrieval.indexer import LegalIndexer
from src.schema import Act

def main():
    print("=" * 80)
    print("VIDHI-AI: COMPLETE DATABASE REBUILD - 368 Acts")
    print("=" * 80)
    
    processed_dir = "data/processed"
    json_files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
    
    print(f"\n📊 Found {len(json_files)} processed JSON files")
    print(f"🔄 Building fresh ChromaDB database...")
    print("=" * 80 + "\n")
    
    # Create fresh indexer (will create new ChromaDB)
    indexer = LegalIndexer()
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    total_chunks = 0
    
    for idx, json_file in enumerate(json_files, 1):
        try:
            # Load Act from JSON
            filepath = os.path.join(processed_dir, json_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                act_data = json.load(f)
            
            # Parse as Act model
            act = Act(**act_data)
            
            # Index it
            indexer.index_act(act)
            success_count += 1
            
            # Progress update every 20 files
            if idx % 20 == 0:
                current_count = indexer.collection.count()
                print(f"Progress: {idx}/{len(json_files)} Acts ({idx*100//len(json_files)}%) | Chunks: {current_count}")
                
        except Exception as e:
            error_msg = str(e)[:150]
            print(f"✗ Error indexing {json_file}: {error_msg}")
            error_count += 1
            continue
    
    elapsed = time.time() - start_time
    
    # Final count
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ DATABASE REBUILD COMPLETE!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   Acts successfully indexed: {success_count}/{len(json_files)}")
    print(f"   Acts with errors: {error_count}")
    print(f"   Total chunks in ChromaDB: {final_count:,}")
    print(f"   Average chunks per Act: {final_count//success_count if success_count > 0 else 0}")
    print(f"\n⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    
    print("\n" + "=" * 80)
    print("🎯 SYSTEM READY!")
    print("   Test with: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
