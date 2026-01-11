#!/usr/bin/env python3
"""
Final ingestion and demo of Vidhi-AI with 9 Acts
"""
import sys
import json
import shutil
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("VIDHI-AI FINAL DEMO: Ingesting 9 Acts")
print("=" * 70)

# Step 1: Reset database
print("\n[1/4] Resetting database...")
if os.path.exists("data/chroma_db"):
    shutil.rmtree("data/chroma_db")
print("✓ Database reset")

# Step 2: Run ingestion
print("\n[2/4] Running ingestion pipeline...")
from src.ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline(raw_data_dir="data/raw")
try:
    pipeline.run_batch()
    print(f"✓ Processed files")
    print(f"  HTML success: {pipeline.stats.get('html_success', 0)}")
    print(f"  PDF success: {pipeline.stats.get('pdf_success', 0)}")
except Exception as e:
    print(f"⚠ Some errors during processing: {e}")

# Step 3: Index everything
print("\n[3/4] Indexing to ChromaDB...")
from src.retrieval.indexer import LegalIndexer
from src.schema import Act

indexer = LegalIndexer()

# Load and index all processed JSON
processed_dir = "data/processed"
if os.path.exists(processed_dir):
    json_files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
    
    for fname in json_files:
        try:
            with open(os.path.join(processed_dir, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
            act = Act(**data)
            indexer.index_act(act)
        except Exception as e:
            print(f"  Skip {fname}: {e}")

total = indexer.collection.count()
print(f"✓ Total indexed: {total} chunks")

# Step 4: Test queries
print("\n[4/4] Testing system...")
from src.reasoning.chain import LegalChain

chain = LegalChain()

test_queries = [
    "What are the requirements?",
    "Election related provisions",
]

for q in test_queries:
    try:
        result = chain.answer(q[:30])
        print(f"\nQ: {q}")
        print(f"A: {result['answer'][:150]}...")
        print(f"Sources: {len(result['sources'])}")
        if result['sources'] and 'clause_number' in result['sources'][0]:
            print(f"✓ Clause-level citations working!")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("DEMO COMPLETE!")
print("=" * 70)
print(f"\nSystem Status:")
print(f"  Acts indexed: {len(json_files) if os.path.exists(processed_dir) else 0}")
print(f"  Total chunks: {total}")
print(f"  Features: Multi-turn chat, Rate limiting, Data lineage, Clause citations")
print("\nReady for queries via:")
print("  - Python: from src.reasoning.chain import LegalChain; chain.answer('...')")
print("  - Test script: python test_enhanced.py")
