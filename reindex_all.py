#!/usr/bin/env python3
"""
Reindex all processed Acts into ChromaDB
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
    print("VIDHI-AI: REINDEXING ALL PROCESSED ACTS")
    print("=" * 80)
    
    processed_dir = "data/processed"
    json_files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
    
    print(f"\n📊 Found {len(json_files)} processed JSON files")
    print(f"🔄 Starting reindexing...")
    print("=" * 80)
    
    indexer = LegalIndexer()
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    
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
            
            if idx % 10 == 0:
                print(f"Progress: {idx}/{len(json_files)} ({idx*100//len(json_files)}%)")
                
        except Exception as e:
            print(f"✗ Error indexing {json_file}: {str(e)[:100]}")
            error_count += 1
    
    elapsed = time.time() - start_time
    
    # Final count
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ REINDEXING COMPLETE!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   - Successfully indexed: {success_count}")
    print(f"   - Errors: {error_count}")
    print(f"   - Total chunks in ChromaDB: {final_count}")
    print(f"\n⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEP: Test the system")
    print("   Run: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
