#!/usr/bin/env python3
"""Full RAG pipeline test with semantic search and LLM"""
import json
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

import os
import requests
from src.retrieval.indexer import LegalIndexer, get_openai_embedding
from src.schema import Act

def test_search():
    """Test semantic search"""
    print("\n=== Testing Semantic Search ===\n")
    
    # Create indexer (to access collection)
    indexer = LegalIndexer()
    count = indexer.collection.count()
    print(f"Total indexed documents: {count}")
    
    # Test queries
    test_queries = [
        "How to get citizenship?",
        "What is marriage age?",
        "property rights",
        "nagarikata"  # Nepali romanized
    ]
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        # Get query embedding
        query_emb = get_openai_embedding([query], api_key)[0]
        
        # Search
        results = indexer.collection.query(
            query_embeddings=[query_emb],
            n_results=2
        )
        
        if results and results['documents'][0]:
            for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"  Result {i+1}:")
                print(f"    Act: {meta['act_title'][:40]}...")
                print(f"    Section: {meta['section_number']}")
                print(f"    Preview: {doc[:80]}...")
        else:
            print("  No results")

def test_llm():
    """Test LLM question answering"""
    print("\n=== Testing LLM Integration ===\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    indexer = LegalIndexer()
    
    question = "How can I get citizenship by descent in Nepal?"
    print(f"Question: {question}")
    
    # Get context via search
    query_emb = get_openai_embedding([question], api_key)[0]
    results = indexer.collection.query(
        query_embeddings=[query_emb],
        n_results=3
    )
    
    context = ""
    if results and results['documents'][0]:
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            context += f"[Source: {meta['act_title']}, Section {meta['section_number']}]\n{doc}\n\n"
    
    print(f"\nContext retrieved: {len(context)} chars")
    
    # Call GPT
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a Nepali legal expert. Answer based ONLY on the provided context. Cite specific sections."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        "temperature": 0
    }
    
    print("\nCalling GPT-4...")
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    if resp.status_code == 200:
        answer = resp.json()['choices'][0]['message']['content']
        print(f"\nAnswer:\n{answer}")
    else:
        print(f"Error: {resp.status_code} - {resp.text[:200]}")

if __name__ == "__main__":
    print("=" * 60)
    print("VIDHI-AI FULL RAG PIPELINE TEST")
    print("=" * 60)
    
    test_search()
    test_llm()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
