#!/usr/bin/env python3
"""
Vidhi-AI Interactive Chat Interface
"""
import sys
import time
sys.path.insert(0, '.')

from src.reasoning.chain import LegalChain
from src.retrieval.indexer import LegalIndexer

def type_writer(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    print("\033[H\033[J")  # Clear screen
    print("""
    ╔══════════════════════════════════════════════════╗
    ║                 VIDHI-AI (विधि-AI)               ║
    ║        Nepal's Legal Research Assistant          ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    print("Initializing system...")
    try:
        indexer = LegalIndexer()
        count = indexer.collection.count()
        chain = LegalChain()
        session_id = chain.create_session()
        
        print(f"✓ System Ready | Indexed: {count} chunks")
        print("\nAsk any legal question in English or Nepali.")
        print("Type 'exit' to quit.\n")
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ Startup Error: {e}")
        return

    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Namaste! Closing Vidhi-AI.")
                break
            
            if not query:
                continue
                
            print("\n🤖 Vidhi-AI thinking...\r", end="")
            
            start_time = time.time()
            result = chain.answer(query, session_id=session_id)
            elapsed = time.time() - start_time
            
            print(f"🤖 Vidhi-AI ({elapsed:.1f}s):\n")
            type_writer(result['answer'])
            
            if result.get('sources'):
                print("\n📚 Sources:")
                seen_sources = set()
                for source in result['sources']:
                    # Create readable source string
                    ref = f"{source['act_title']}"
                    if 'section_number' in source:
                        ref += f", Sec {source['section_number']}"
                    if 'clause_number' in source:
                        ref += f", Cl {source['clause_number']}"
                    
                    if ref not in seen_sources:
                        print(f"   • {ref}")
                        seen_sources.add(ref)
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Namaste! Closing Vidhi-AI.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
