#!/usr/bin/env python3
"""Test live queries"""
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
import os
from src.retrieval.indexer import LegalIndexer, get_openai_embedding

# Test queries
queries = [
    'What is the marriage age in Nepal?',
    'How to get citizenship?',
    'Property rights'
]

api_key = os.getenv('OPENAI_API_KEY')
indexer = LegalIndexer()

for q in queries:
    print(f'Query: {q}')
    emb = get_openai_embedding([q], api_key)[0]
    results = indexer.collection.query(query_embeddings=[emb], n_results=2)
    if results and results['documents'][0]:
        for meta in results['metadatas'][0]:
            print(f"  -> Section {meta['section_number']} from {meta['act_title'][:30]}...")
    print()
