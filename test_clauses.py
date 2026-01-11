#!/usr/bin/env python3
"""
Test clause-level indexing and citations
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

import json
from src.retrieval.indexer import LegalIndexer
from src.schema import Act
from src.reasoning.chain import LegalChain

print("=" * 60)
print("CLAUSE-LEVEL INDEXING TEST")
print("=" * 60)

# Reset database
import shutil
import os
if os.path.exists("data/chroma_db"):
    shutil.rmtree("data/chroma_db")
    print("\n✓ Reset ChromaDB\n")

# Load and index sample Act
indexer = LegalIndexer()

print("Step 1: Loading sample data...")
with open('data/processed/sample_citizenship_act.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

act = Act(**data)
print(f"✓ Loaded: {act.title}")
print(f"  Parts: {len(act.parts)}")
print(f"  Chapters: {len(act.chapters)}")

# Count sections and clauses
total_sections = sum(len(ch.sections) for p in act.parts for ch in p.chapters)
total_sections += sum(len(ch.sections) for ch in act.chapters)
print(f"  Sections: {total_sections}")

# Check if clauses exist
sample_section = None
if act.chapters and act.chapters[0].sections:
    sample_section = act.chapters[0].sections[0]
elif act.parts and act.parts[0].chapters and act.parts[0].chapters[0].sections:
    sample_section = act.parts[0].chapters[0].sections[0]

if sample_section:
    print(f"  Sample section clauses: {len(sample_section.clauses)}")
    if sample_section.clauses:
        print(f"    First clause: {sample_section.clauses[0].clause_id}")

print("\nStep 2: Indexing...")
indexer.index_act(act)

count = indexer. collection.count()
print(f"\n✓ Total indexed chunks: {count}")

# Test query with clause retrieval
print("\n" + "=" * 60)
print("CLAUSE CITATION TEST")
print("=" * 60)

chain = LegalChain()
result = chain.answer("How to get citizenship by descent?")

print(f"\nQuery: How to get citizenship by descent?")
print(f"\nAnswer:\n{result['answer'][:300]}...")
print(f"\nCitations:\n{result['citations']}")
print(f"\nSources ({len(result['sources'])}):")
for i, src in enumerate(result['sources'][:3], 1):
    print(f"  {i}. दफा {src['section_number']}", end="")
    if 'clause_number' in src:
        print(f", खण्ड {src['clause_number']}")
    else:
        print()

print("\n" + "=" * 60)
if any('clause_number' in s for s in result['sources']):
    print("✅ CLAUSE-LEVEL CITATIONS WORKING!")
else:
    print("⚠️  No clauses detected (sections indexed only)")
print("=" * 60)
