#!/usr/bin/env python3
"""Test full QA with GPT-4"""
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
import os
import requests
from src.retrieval.indexer import LegalIndexer, get_openai_embedding

api_key = os.getenv('OPENAI_API_KEY')
indexer = LegalIndexer()

question = "What is the legal age for marriage in Nepal according to the law?"
print(f"Question: {question}\n")

# Search
emb = get_openai_embedding([question], api_key)[0]
results = indexer.collection.query(query_embeddings=[emb], n_results=3)

# Build context
context = ""
for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
    context += f"[{meta['act_title']}, Section {meta['section_number']}]\n{doc}\n\n"

print(f"Context retrieved ({len(context)} chars):\n")
print(context[:500] + "...\n")

# Call GPT-4
url = "https://api.openai.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are a Nepali legal expert. Answer based ONLY on the provided context. Always cite the specific Act and Section number."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ],
    "temperature": 0
}

print("Calling GPT-4...\n")
resp = requests.post(url, headers=headers, json=data, timeout=60)
if resp.status_code == 200:
    answer = resp.json()['choices'][0]['message']['content']
    print("=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(answer)
else:
    print(f"Error: {resp.status_code}")
