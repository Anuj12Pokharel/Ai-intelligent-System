import sys
import json
import traceback
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

try:
    print("Step 1: Loading imports...")
    from src.retrieval.indexer import LegalIndexer
    from src.schema import Act
    print("Step 1: OK")
    
    print("Step 2: Loading sample data...")
    with open('data/processed/sample_citizenship_act.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    act = Act(**data)
    print(f"Step 2: OK - Title: {act.title[:30]}...")
    
    print("Step 3: Creating indexer...")
    indexer = LegalIndexer()
    print("Step 3: OK")
    
    print("Step 4: Indexing act...")
    indexer.index_act(act)
    print("Step 4: OK")
    
    print("Step 5: Checking count...")
    count = indexer.collection.count()
    print(f"Step 5: OK - Count: {count}")
    
    print("\n=== SUCCESS! ===")
    
except Exception as e:
    print(f"\nERROR at current step: {type(e).__name__}: {e}")
    traceback.print_exc()
