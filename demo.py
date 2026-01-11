#!/usr/bin/env python3
"""
Quick demo of Vidhi-AI with indexed 9 Acts
"""
import sys
sys.path.insert(0, '.')

from src.reasoning.chain import LegalChain
from src.retrieval.indexer import LegalIndexer

print("=" * 70)
print("VIDHI-AI LIVE DEMO")
print("=" * 70)

# Check what's indexed
indexer = LegalIndexer()
count = indexer.collection.count()
print(f"\n✓ System Status:")
print(f"  Indexed chunks: {count}")

# Create chain
chain = LegalChain()

# Test 1: Simple query
print("\n" + "=" * 70)
print("TEST 1: Single Query")
print("=" * 70)

question1 = "What are the main provisions?"
print(f"\nQ: {question1}")
result1 = chain.answer(question1)
print(f"\nA: {result1['answer'][:300]}...")
print(f"\n📊 Stats:")
print(f"  Latency: {result1['latency_ms']} ms")
print(f"  Tokens: {result1['tokens_used']}")
print(f"  Sources: {len(result1['sources'])}")

# Check for clause-level citations
if result1['sources'] and 'clause_number' in result1['sources'][0]:
    print(f"  ✅ Clause-level citation!")
    print(f"  खण्ड {result1['sources'][0]['clause_number']}")

# Test 2: Multi-turn
print("\n" + "=" * 70)
print("TEST 2: Multi-Turn Conversation")
print("=" * 70)

session_id = chain.create_session()
print(f"\n✓ Session created: {session_id[:16]}...")

q1 = "Tell me about elections"
r1 = chain.answer(q1, session_id=session_id)
print(f"\nTurn 1:")
print(f"Q: {q1}")
print(f"A: {r1['answer'][:150]}...")

q2 = "What are the requirements?"
r2 = chain.answer(q2, session_id=session_id)
print(f"\nTurn 2 (with context):")
print(f"Q: {q2}")
print(f"A: {r2['answer'][:150]}...")

# Final stats
print("\n" + "=" * 70)
print("SYSTEM STATS")
print("=" * 70)
stats = chain.get_stats()
print(f"\nLineage:")
print(f"  Total queries: {stats['lineage']['total_traces']}")
if stats['lineage']['total_traces'] > 0:
    print(f"  Avg latency: {stats['lineage']['average_latency_ms']:.1f} ms")

print(f"\nMetrics:")
for key, value in stats['metrics'].items():
    if 'api' in key.lower():
        print(f"  {key}: {value}")

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE - System Working!")
print("=" * 70)
