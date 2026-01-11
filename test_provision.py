import sys
sys.path.insert(0, '.')
from src.reasoning.chain import LegalChain

def test_provision():
    print("Initializing Legal Chain...")
    chain = LegalChain()
    
    # Query about Company Act since we saw it indexed
    question = "कम्पनी दर्ता गर्न के के कागजात चाहिन्छ? (What documents are needed to register a company?)"
    print(f"\n❓ Question: {question}")
    print("-" * 50)
    
    response = chain.answer(question)
    
    print(f"\n🤖 Answer:\n{response['answer']}")
    print("\n📚 Sources:")
    for source in response['sources']:
        print(f"- {source}")

if __name__ == "__main__":
    test_provision()
