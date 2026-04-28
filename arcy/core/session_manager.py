"""
SessionManager — Arcy's Chat Log Storage
Handles saving, loading, and listing chat sessions.
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime

# Sessions directory
DATA_DIR = Path("data")
SESSIONS_DIR = DATA_DIR / "sessions"
INDEX_FILE = SESSIONS_DIR / "index.json"

def ensure_session_dir():
    """Ensure the session folder exists."""
    if not SESSIONS_DIR.exists():
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def save_session(session_id: str, messages: list, title: str = None):
    """Save a full transcript to a JSON file."""
    ensure_session_dir()
    
    file_path = SESSIONS_DIR / f"{session_id}.json"
    
    # Save the full transcript
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)
    
    # Update the index
    update_session_index(session_id, title)

def update_session_index(session_id: str, title: str = None):
    """Update the index file with session metadata."""
    index = load_session_index()
    
    # If session doesn't exist, create it
    if session_id not in index:
        index[session_id] = {
            "id": session_id,
            "title": title or "New Chat",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    else:
        # Update existing session
        if title:
            index[session_id]["title"] = title
        index[session_id]["updated_at"] = datetime.now().isoformat()
    
    # Sort by updated_at descending
    sorted_index = dict(sorted(index.items(), key=lambda x: x[1]['updated_at'], reverse=True))
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_index, f, indent=4)

def load_session_index() -> dict:
    """Get the session metadata index."""
    if not INDEX_FILE.exists():
        return {}
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_messages(session_id: str) -> list:
    """Load a full transcript from a JSON file."""
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def delete_session(session_id: str):
    """Remove a session from disk and index."""
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if file_path.exists():
        os.remove(file_path)
    
    index = load_session_index()
    if session_id in index:
        del index[session_id]
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=4)
