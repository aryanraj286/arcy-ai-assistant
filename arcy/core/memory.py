"""
Arcy — Conversation Memory
Maintains short-term conversation context and long-term vector memory (ChromaDB).
"""

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import chromadb
from pathlib import Path

@dataclass
class Turn:
    role: Literal["user", "assistant"]
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConversationMemory:
    """
    Maintains a rolling window of conversation turns (short-term)
    and a vector database (long-term) to recall past context.
    """

    def __init__(self, max_turns: int = 20):
        self._turns: deque[Turn] = deque(maxlen=max_turns)
        
        # Initialize Long-term memory (ChromaDB)
        try:
            data_path = Path("./data/chroma")
            data_path.parent.mkdir(exist_ok=True, parents=True)
            self.client = chromadb.PersistentClient(path=str(data_path))
            self.collection = self.client.get_or_create_collection(name="arcy_long_term")
            print("[Memory] Long-term memory brain initialized.")
        except Exception as e:
            print(f"[Memory] ChromaDB init error: {str(e)}")
            self.collection = None

    def add_user(self, text: str):
        """Add a user message to both short and long-term memory."""
        turn = Turn(role="user", content=text)
        self._turns.append(turn)
        self._store_in_vector_db(text, "user", turn.timestamp)

    def add_assistant(self, text: str):
        """Add an assistant message to both short and long-term memory."""
        turn = Turn(role="assistant", content=text)
        self._turns.append(turn)
        self._store_in_vector_db(text, "assistant", turn.timestamp)

    def _store_in_vector_db(self, text: str, role: str, timestamp: str):
        """Hidden persistence into ChromaDB."""
        if self.collection and text and len(text.strip()) > 5:
            try:
                self.collection.add(
                    documents=[text],
                    metadatas=[{"role": role, "timestamp": timestamp}],
                    ids=[str(uuid.uuid4())]
                )
            except Exception as e:
                print(f"[Memory] Vector storage error: {e}")

    def query_long_term(self, query_text: str, n_results: int = 2) -> str:
        """Recall relevant snippets from the past based on the current query."""
        if not self.collection or not query_text:
            return ""
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            docs = results.get("documents", [[]])[0]
            if not docs:
                return ""
            
            # Filter matches to avoid repetitive loops if they match the current query too closely
            unique_docs = [d for d in docs if d.strip().lower() != query_text.strip().lower()]
            if not unique_docs:
                return ""

            context_block = "\n[Historical Context]:\n" + "\n".join([f"- {d}" for d in unique_docs])
            return context_block
        except:
            return ""

    def to_messages(self) -> list[dict]:
        """Convert turns to message list for LLM consumption."""
        return [{"role": t.role, "content": t.content} for t in self._turns]

    def load_from_list(self, message_list: list):
        """Populate short-term memory from a list of dicts (e.g., from a session file)."""
        self.clear()
        for msg in message_list:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                self._turns.append(Turn(role=role, content=content))

    def clear(self):
        """Clear the rolling window (short-term memory)."""
        self._turns.clear()

    def __len__(self):
        return len(self._turns)
