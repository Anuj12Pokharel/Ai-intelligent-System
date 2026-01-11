#!/usr/bin/env python3
"""
Test: Parse ONE Act and try to index it, checking each step
"""
import sys
sys.path.insert(0, '.')
from src.ingestion.parser import NepaliLegalParser
from src.retrieval.indexer import LegalIndexer
import os

files = [f for f in os.listdir('data/raw') if f.endswith('.pdf')]
filepath = f'data/raw/{files[0]}'

print("1. Parsing PDF...")
parser = NepaliLegalParser(filepath)
act = parser.parse()

print(f"✓ Parsed: {act.title[:50]}")
print(f"  Parts: {len(act.parts)}, Chapters: {len(act.chapters)}")

# Count sections
total_sections = 0
for part in act.parts:
    for chapter in part.chapters:
        total_sections += len(chapter.sections)
for chapter in act.chapters:
    total_sections += len(chapter.sections)

print(f"  Total sections: {total_sections}")

if total_sections == 0:
    print("\n❌ NO SECTIONS FOUND - Cannot index!")
else:
    print("\n2. Attempting to index...")
    indexer = LegalIndexer()
    
    try:
        indexer.index_act(act)
        print("✓ index_act() completed")
        
        count = indexer.collection.count()
        print(f"\n3. ChromaDB check:")
        print(f"   Chunks: {count}")
        
        if count > 0:
            print("\n✅ SUCCESS - Chunks created!")
        else:
            print("\n❌ PROBLEM - index_act ran but no chunks created")
            
    except Exception as e:
        print(f"\n❌ ERROR during indexing: {e}")
        import traceback
        traceback.print_exc()
