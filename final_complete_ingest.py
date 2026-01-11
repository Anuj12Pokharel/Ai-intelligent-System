#!/usr/bin/env python3
"""
FINAL Complete Ingestion: Process all 369 raw files directly to ChromaDB
"""
import sys
import os
import time
sys.path.insert(0, '.')

from src.ingestion.pipeline import IngestionPipeline

def main():
    print("=" * 80)
    print("VIDHI-AI: FINAL COMPLETE INGESTION - 369 Acts")
    print("=" * 80)
    
    # Count raw files
    raw_dir = "data/raw"
    files = [f for f in os.listdir(raw_dir) if f.endswith(('.pdf', '.html', '.htm'))]
    
    print(f"\n📊 Raw files to process: {len(files)}")
    print(f"   PDFs: {sum(1 for f in files if f.endswith('.pdf'))}")
    print(f"   HTML: {sum(1 for f in files if f.endswith(('.html', '.htm')))}")
    print(f"\n🔄 Starting fresh ingestion pipeline...")
    print(f"   - Parsing with clause extraction")
    print(f"   - Indexing directly to ChromaDB")
    print("=" * 80 + "\n")
    
    start_time = time.time()
    
    # Run pipeline
    pipeline = IngestionPipeline()
    pipeline.run_batch()
    
    elapsed = time.time() - start_time
    
    # Get final stats from indexer
    from src.retrieval.indexer import LegalIndexer
    indexer = LegalIndexer()
    final_count = indexer.collection.count()
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE INGESTION FINISHED!")
    print("=" * 80)
    print(f"\n📈 Final Results:")
    print(f"   Total chunks indexed: {final_count:,}")
    print(f"   Files processed: {pipeline.stats.get('total_files', 0)}")
    print(f"   Success rate: {pipeline.stats.get('success_count', 0)}/{pipeline.stats.get('total_files', 0)}")
    print(f"\n⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    
    print("\n" + "=" * 80)
    print("🎯 VIDHI-AI SYSTEM IS NOW READY!")
    print("   Test with: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
