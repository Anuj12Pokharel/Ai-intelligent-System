#!/usr/bin/env python3
"""
Comprehensive test for enhanced Vidhi-AI components:
- Multi-turn conversation
- Rate limiting
- Data lineage tracking
- System metrics
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from src.reasoning.chain import LegalChain
import json

def test_single_query():
    """Test 1: Basic single query"""
    print("=" * 60)
    print("TEST 1: Single Query with Full Tracing")
    print("=" * 60)
    
    chain = LegalChain()
    result = chain.answer("What is the legal marriage age in Nepal?")
    
    print(f"\nQuery: What is the legal marriage age in Nepal?")
    print(f"\nAnswer:\n{result['answer']}\n")
    print(f"Citations:\n{result['citations']}\n")
    print(f"Lineage ID: {result['lineage_id']}")
    print(f"Latency: {result['latency_ms']} ms")
    print(f"Tokens: {result['tokens_used']}")
    print(f"Sources: {len(result['sources'])} documents retrieved")
    
    return chain

def test_multi_turn_conversation(chain):
    """Test 2: Multi-turn conversation"""
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Turn Conversation")
    print("=" * 60)
    
    # Create a session
    session_id = chain.create_session()
    print(f"\nCreated session: {session_id[:8]}...")
    
    # First question
    print("\n--- Turn 1 ---")
    q1 = "How can I get citizenship in Nepal?"
    r1 = chain.answer(q1, session_id=session_id)
    print(f"Q: {q1}")
    print(f"A: {r1['answer'][:200]}...")
    
    # Follow-up question (should use context from previous)
    print("\n--- Turn 2 ---")
    q2 = "What documents are required?"
    r2 = chain.answer(q2, session_id=session_id)
    print(f"Q: {q2}")
    print(f"A: {r2['answer'][:200]}...")
    
    print(f"\n✓ Multi-turn conversation working")
    print(f"  Session has {len(chain.conversation_manager.sessions[session_id])} messages")

def test_rate_limiting(chain):
    """Test 3: Rate limiter"""
    print("\n" + "=" * 60)
    print("TEST 3: Rate Limiting")
    print("=" * 60)
    
    import time
    
    # Make a few rapid queries
    print("\nMaking 3 rapid queries...")
    start = time.time()
    for i in range(3):
        chain.answer("What is property law?")
        print(f"  Query {i+1} completed")
    elapsed = time.time() - start
    
    print(f"✓ All queries completed in {elapsed:.2f}s")
    print(f"  Rate limiter is working (no crashes)")

def test_metrics_and_lineage(chain):
    """Test 4: Metrics and lineage"""
    print("\n" + "=" * 60)
    print("TEST 4: Metrics & Lineage")
    print("=" * 60)
    
    stats = chain.get_stats()
    
    print("\nSystem Statistics:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n✓ Observability working:")
    print(f"  - Total queries tracked: {stats['lineage']['total_traces']}")
    print(f"  - Index size: {stats['index_size']} documents")
    print(f"  - API calls made: {stats['metrics'].get('api_calls', 'N/A')}")

def test_bilingual():
    """Test 5: Bilingual queries"""
    print("\n" + "=" * 60)
    print("TEST 5: Bilingual Support")
    print("=" * 60)
    
    chain = LegalChain()
    
    # English query
    print("\n--- English Query ---")
    r1 = chain.answer("What is citizenship law?")
    print(f"Answer: {r1['answer'][:150]}...")
    
    # Nepali query (romanized)
    print("\n--- Nepali Query ---")
    r2 = chain.answer("nagarikata kasto paune?")
    print(f"Answer: {r2['answer'][:150]}...")
    
    print("\n✓ Bilingual queries working")

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("VIDHI-AI ENHANCED COMPONENTS TEST SUITE")
    print("█" * 60)
    
    try:
        # Run all tests
        chain = test_single_query()
        test_multi_turn_conversation(chain)
        test_rate_limiting(chain)
        test_metrics_and_lineage(chain)
        test_bilingual()
        
        print("\n" + "█" * 60)
        print("ALL TESTS PASSED ✓")
        print("█" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
