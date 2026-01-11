#!/usr/bin/env python3
"""
Test if ChromaDB database is working at all
"""
import sys
sys.path.insert(0, '.')

from src.retrieval.indexer import LegalIndexer
from src.schema import Act, Part, Chapter, Section, Clause

def main():
    print("=" * 80)
    print("DATABASE TEST: Creating simple test Act")
    print("=" * 80)
    
    # Create a simple test Act manually
    test_act = Act(
        title="Test Act 2081",
        year="2081",
        source_url="test",
        parts=[Part(
            part_number="1",
            title="Test Part",
            chapters=[Chapter(
                chapter_number="1",
                title="Test Chapter",
                sections=[Section(
                    section_number="1",
                    title="Test Section",
                    content="This is a test section content",
                    clauses=[
                        Clause(clause_id="1", content="First test clause"),
                        Clause(clause_id="2", content="Second test clause")
                    ]
                )]
            )]
        )]
    )
    
    print("\n✓ Created test Act with 1 section and 2 clauses")
    print("\n🔄 Attempting to index...")
    
    try:
        indexer = LegalIndexer()
        print(f"✓ Indexer initialized")
        print(f"   Collection: {indexer.collection_name}")
        print(f"   Persist dir: {indexer.persist_directory}")
        
        indexer.index_act(test_act)
        print("✓ index_act() completed without error")
        
        count = indexer.collection.count()
        print(f"\n📊 ChromaDB Status:")
        print(f"   Total chunks: {count}")
        
        if count > 0:
            print("\n✅ DATABASE IS WORKING!")
            print("   The issue is with parsing the raw files, not ChromaDB")
        else:
            print("\n❌ DATABASE PROBLEM CONFIRMED!")
            print("   ChromaDB is not storing chunks even when explicitly called")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
