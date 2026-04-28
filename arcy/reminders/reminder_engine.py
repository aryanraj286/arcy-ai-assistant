"""
Arcy — Reminder Engine
Create, list, delete, and trigger reminders.
Parses time references from natural language using dateparser.
Data is persisted locally as JSON.
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid

try:
    import dateparser
    HAS_DATEPARSER = True
except ImportError:
    HAS_DATEPARSER = False

# Reminder storage path
STORE_PATH = Path(__file__).parent / "reminder_store.json"


def _load() -> list[dict]:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(reminders: list[dict]):
    STORE_PATH.write_text(
        json.dumps(reminders, indent=2, default=str),
        encoding="utf-8"
    )


def add_reminder(text: str, time_expression: str = None) -> str:
    """
    Add a reminder.

    Args:
        text: What to remind about (e.g. "call dad")
        time_expression: Natural language time (e.g. "tomorrow at 9am", "Friday 6pm")
                         If None, reminder is saved without a specific time.

    Returns:
        Confirmation message for Arcy to speak
    """
    reminders = _load()

    due_dt = None
    due_str = "whenever you ask"

    if time_expression and HAS_DATEPARSER:
        parsed = dateparser.parse(
            time_expression,
            settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False}
        )
        if parsed:
            due_dt = parsed.isoformat()
            due_str = parsed.strftime("%A, %d %B at %I:%M %p")

    reminder = {
        "id": str(uuid.uuid4())[:8],
        "text": text,
        "due": due_dt,
        "due_display": due_str,
        "created": datetime.now().isoformat(),
        "done": False,
    }
    reminders.append(reminder)
    _save(reminders)

    return f"Got it. I'll remind you about '{text}' — {due_str}."


def get_due_reminders() -> list[dict]:
    """Return reminders that are due now (within the last hour or past due)."""
    reminders = _load()
    now = datetime.now()
    due = []
    for r in reminders:
        if r.get("done") or not r.get("due"):
            continue
        due_dt = datetime.fromisoformat(r["due"])
        if due_dt <= now:
            due.append(r)
    return due


def list_reminders() -> str:
    """Return a spoken summary of all pending reminders."""
    reminders = [r for r in _load() if not r.get("done")]
    if not reminders:
        return "You have no reminders set right now."

    if len(reminders) == 1:
        r = reminders[0]
        return f"You have one reminder: '{r['text']}' — {r['due_display']}."

    lines = [f"You have {len(reminders)} reminders:"]
    for i, r in enumerate(reminders, 1):
        lines.append(f"{i}. {r['text']} — {r['due_display']}")
    return " ".join(lines)


def clear_all_reminders() -> str:
    """Wipe all reminders."""
    _save([])
    return "All reminders have been cleared, Sir."


def remove_reminder_by_text(search_text: str) -> str:
    """Attempts to find and remove reminders that match the given text."""
    reminders = _load()
    if not reminders:
        return "You have no reminders to remove, Sir."
    
    search_text = search_text.lower().strip()
    # Basic matching logic: "call dad" matches "call dad tomorrow"
    remaining = [r for r in reminders if search_text not in r["text"].lower() 
                 and r["text"].lower() not in search_text]
    
    if len(remaining) < len(reminders):
        removed_count = len(reminders) - len(remaining)
        _save(remaining)
        return f"Certainly, Sir. I've removed {removed_count} matching reminder{'s' if removed_count > 1 else ''}."
    
    return f"I couldn't find any reminders matching '{search_text}', Sir."


def extract_reminder_from_text(text: str) -> tuple[str, str]:
    """
    Basic extraction of reminder content and time from natural language.
    e.g. "remind me to call dad at 9pm" → ("call dad", "9pm")

    Returns:
        (reminder_text, time_expression)
    """
    import re

    # Patterns to strip: "remind me to", "remind me about", "set a reminder for"
    text = re.sub(
        r"(remind me (to|about|that|of)?|set (a )?reminder (for|to|about)?|delete|remove|clear|forget about)\s*",
        "", text, flags=re.IGNORECASE
    ).strip()

    # Split on time indicators
    time_pattern = re.compile(
        r"\s+(at|on|by|in|tomorrow|tonight|this|next|every)\s+",
        re.IGNORECASE
    )
    match = time_pattern.search(text)
    if match:
        reminder_text = text[:match.start()].strip()
        time_expr = text[match.start():].strip()
    else:
        reminder_text = text
        time_expr = None

    return reminder_text or text, time_expr
