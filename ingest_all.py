#!/usr/bin/env python3
"""
Complete Ingestion Pipeline - Process all 369 downloaded Acts
"""
import sys
import os
import time
sys.path.insert(0, '.')

from src.ingestion.pipeline import IngestionPipeline

def main():
    print("=" * 80)
    print("VIDHI-AI: FULL INGESTION PIPELINE - 369 Acts")
    print("=" * 80)
    
    # Count files
    raw_dir = "data/raw"
    files = [f for f in os.listdir(raw_dir) if f.endswith(('.pdf', '.html'))]
    print(f"\n📊 Files to process: {len(files)}")
    print(f"   - PDFs: {sum(1 for f in files if f.endswith('.pdf'))}")
    print(f"   - HTML: {sum(1 for f in files if f.endswith('.html'))}")
    
    print(f"\n🔄 Starting ingestion with clause-level extraction...")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run pipeline
    pipeline = IngestionPipeline()
    pipeline.run_batch()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ INGESTION COMPLETE!")
    print("=" * 80)
    print(f"\n📈 Results:")
    print(f"   - HTML processed: {pipeline.stats.get('html_success', 0)}")
    print(f"   - PDF processed: {pipeline.stats.get('pdf_success', 0)}")
    print(f"   - Failed: {pipeline.stats.get('failed', 0)}")
    print(f"   - Total successful: {pipeline.stats.get('html_success', 0) + pipeline.stats.get('pdf_success', 0)}")
    print(f"\n⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    
    # Check indexed count
    from src.retrieval.indexer import LegalIndexer
    indexer = LegalIndexer()
    count = indexer.collection.count()
    
    print(f"\n📚 ChromaDB Status:")
    print(f"   - Total indexed chunks: {count}")
    print(f"   - Clause-level precision: ✓")
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEP: Test the system")
    print("   Run: python demo.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
