import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Simple in-memory conversation manager for multi-turn chat

@dataclass
class Message:
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[List[Dict]] = None

class ConversationManager:
    def __init__(self):
        # session_id -> list of Message
        self.sessions: Dict[str, List[Message]] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id

    def add_message(self, session_id: str, role: str, content: str, sources: Optional[List[Dict]] = None):
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} does not exist")
        self.sessions[session_id].append(Message(role, content, sources))

    def get_history(self, session_id: str, limit: int = 5) -> List[Message]:
        # Return the most recent messages up to limit
        return self.sessions.get(session_id, [])[-limit:]

    def build_gpt_messages(self, session_id: str, system_prompt: str, context: str, user_query: str) -> List[Dict]:
        """Construct the message list for OpenAI API.
        Includes system prompt, recent conversation history, context, and current query.
        """
        messages: List[Dict] = [{"role": "system", "content": system_prompt}]
        # Add recent conversation history (assistant and user messages)
        history = self.get_history(session_id)
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        # Add context as a user message (helps LLM see the retrieved docs)
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"})
        return messages
