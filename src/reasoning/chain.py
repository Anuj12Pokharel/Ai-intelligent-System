"""
Enhanced Legal Chain with Multi-turn Conversation, Rate Limiting, and Data Lineage
"""
import os
import time
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Import new components
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.retrieval.indexer import LegalIndexer, get_openai_embedding
from src.reasoning.conversation import ConversationManager
from src.utils.rate_limiter import get_rate_limiter, with_retry
from src.utils.lineage import LineageTracker
from src.utils.metrics import get_metrics, Metrics

SYSTEM_PROMPT = """You are Vidhi-AI, a Nepali Legal Assistant specialized in Nepal's legal framework.

INSTRUCTIONS:
1. Answer questions based ONLY on the provided legal context.
2. ALWAYS cite the specific Act, Chapter (परिच्छेद), Section (दफा), and Clause (खण्ड) for every claim.
3. If the answer is not in the context, state: "I cannot find relevant legal provisions in my indexed documents."
4. Answer in the language of the user's query (English or Nepali/नेपाली).
5. Maintain formal legal tone appropriate for legal consultation.
6. For follow-up questions, use the conversation history to understand context.

CITATION FORMAT:
- English: [Act Name, Section X, Clause Y]
- Nepali: [ऐनको नाम, दफा X, खण्ड Y]
"""

class LegalChain:
    """
    Production-ready legal QA chain with full observability
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        self.indexer = LegalIndexer()
        self.conversation_manager = ConversationManager()
        self.lineage_tracker = LineageTracker()
        self.rate_limiter = get_rate_limiter()
        self.metrics = get_metrics()
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        return self.conversation_manager.create_session()
    
    def _search(self, query: str, k: int = 5) -> tuple:
        """Search for relevant documents"""
        start = time.time()
        emb = get_openai_embedding([query], self.api_key)[0]
        results = self.indexer.collection.query(
            query_embeddings=[emb],
            n_results=k
        )
        self.metrics.record(Metrics.EMBEDDING_LATENCY, (time.time() - start) * 1000)
        return results
    
    def _build_context(self, results: Dict) -> tuple:
        """Build context string and source metadata"""
        context_parts = []
        sources = []
        
        if results and results['documents'][0]:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                context_parts.append(
                    f"[Source: {meta['act_title']}, दफा {meta['section_number']}]\n{doc}"
                )
                sources.append(meta)
        
        return "\n\n".join(context_parts), sources
    
    @with_retry(max_retries=3)
    def _call_llm(self, messages: List[Dict]) -> Dict:
        """Call OpenAI API with rate limiting"""
        self.rate_limiter.wait_if_needed()
        self.metrics.increment(Metrics.API_CALLS)
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code != 200:
            self.metrics.increment(Metrics.API_ERRORS)
            raise Exception(f"API error: {response.status_code}")
        
        result = response.json()
        tokens = result.get('usage', {}).get('total_tokens', 0)
        self.metrics.increment(Metrics.TOKENS_USED, tokens)
        
        return result
    
    def answer(self, query: str, session_id: Optional[str] = None) -> Dict:
        """
        Answer a legal question with full tracing
        
        Returns:
            Dict with answer, sources, and lineage
        """
        start = time.time()
        
        # Start lineage tracking
        lineage = self.lineage_tracker.start_trace(query)
        
        # Search for context
        results = self._search(query)
        context, sources = self._build_context(results)
        
        # Add sources to lineage
        self.lineage_tracker.add_sources(lineage, sources)
        
        # Build messages (with conversation history if session provided)
        if session_id:
            messages = self.conversation_manager.build_gpt_messages(
                session_id, SYSTEM_PROMPT, context, query
            )
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
        
        # Call LLM
        result = self._call_llm(messages)
        answer = result['choices'][0]['message']['content']
        tokens = result.get('usage', {}).get('total_tokens', 0)
        
        # Complete lineage
        latency = (time.time() - start) * 1000
        self.lineage_tracker.complete_trace(lineage, answer, latency, tokens)
        self.metrics.record(Metrics.QUERY_LATENCY, latency)
        
        # Update conversation history if using sessions
        if session_id:
            self.conversation_manager.add_message(session_id, "user", query)
            self.conversation_manager.add_message(session_id, "assistant", answer, sources)
        
        # Build citation path
        citations = self.lineage_tracker.get_citation_path(lineage)
        
        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
            "lineage_id": lineage.lineage_id,
            "latency_ms": round(latency, 2),
            "tokens_used": tokens
        }
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "lineage": self.lineage_tracker.get_stats(),
            "metrics": self.metrics.get_summary(),
            "index_size": self.indexer.collection.count()
        }

if __name__ == "__main__":
    chain = LegalChain()
    result = chain.answer("What is the marriage age in Nepal?")
    print(result)

