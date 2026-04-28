"""
Arcy — Intent Router
Classifies user input into intents and routes to the correct handler.
Uses keyword matching + Azure NLP key phrases. No ML training needed.
"""

import re
from typing import Callable


# ─────────────────────────────────────────────────────────────
# Intent Definitions
# Each intent has a list of trigger patterns (regex or keywords).
# ─────────────────────────────────────────────────────────────
INTENTS = {
    "weather_query": [
        r"\bweather\b", r"\bforecast\b", r"\brain\b", r"\bsunny\b",
        r"\btemperature\b", r"\bhot\b", r"\bcold\b", r"\bwind\b",
        r"\bhumidity\b", r"\bwhat.s it like outside\b",
    ],
    "news_query": [
        r"\bnews\b", r"\bheadlines\b", r"\bwhat.s happening\b",
        r"\blatest\b", r"\bcurrent events\b", r"\bbreaking\b",
    ],
    "clear_reminders": [
        r"\b(delete|remove|clear|cancel|wipe|forget)\b.*(reminders?|remind me|everything)\b",
        r"\bforget about.*\b", r"\bremove that\b", r"\bclear all\b"
    ],
    "set_reminder": [
        r"\bremind\b", r"\breminder\b", r"\bdon.t let me forget\b",
        r"\bset.*(alarm|reminder|alert)\b", r"\btell me (at|when|to)\b",
    ],
    "list_reminders": [
        r"\b(my|show|list|what).*(reminders?|tasks?|schedule)\b",
        r"\bwhat do i have\b", r"\banything due\b", r"\bwhat.s (due|upcoming)\b",
    ],
    "daily_plan": [
        r"\bwhat should i do\b", r"\bplan (for )?today\b",
        r"\bmy (day|schedule|agenda)\b", r"\btoday.s plan\b",
    ],
    "time_query": [
        r"\bwhat time\b", r"\bwhat.s the time\b", r"\bcurrent time\b",
    ],
    "date_query": [
        r"\bwhat.s (the |today.s )?date\b", r"\bwhat day is it\b",
        r"\btoday.s date\b",
    ],
    "greet_arcy": [
        r"\bhey arcy\b", r"\bhello arcy\b", r"\bhi arcy\b",
        r"\bwake up\b", r"\bget ready\b",
    ],
    "emotional_support": [
        r"\bi.?m (stressed|anxious|sad|depressed|upset|tired|frustrated|angry|worried)\b",
        r"\bi am (stressed|anxious|sad|depressed|upset|tired|frustrated|angry|worried)\b",
        r"\bi feel (bad|terrible|awful|lost|overwhelmed|alone|stressed|anxious)\b",
        r"\bfeeling (stressed|anxious|sad|depressed|upset|overwhelmed|lost)\b",
        r"\bmy (life|day) (is |.* )(hard|difficult|rough|terrible)\b",
        r"\b(stressed|anxious|depressed|overwhelmed) (about|with|over)\b",
    ],
    "web_search": [
        r"\bsearch\b.*(on|in|google|youtube|bing|chrome|edge)\b", 
        r"\bgoogle\s+(it|this)\b", r"\bfind\s+(information|about|on)\b", 
        r"\blook up\b", r"\bgive me .* (on|about|from|in) \b(google|youtube|bing)\b"
    ],
    "open_command": [
        r"\b(open|launch|start|run)\b.*(file|folder|app|application|program|chrome|firefox|edge|notepad|calculator|youtube|gmail|github|spotify|discord|whatsapp|telegram|vs\s*code|vscode|explorer|downloads|documents|desktop|pictures|music|videos|terminal|powershell|cmd|word|excel|powerpoint|vlc|maps|drive|translate|netflix|instagram|twitter|linkedin)\b",
        r"\b(open|launch|start)\s+\w",   # "open <anything>" — wide catch
        r"\bgo to\b", r"\bnavigate to\b",
        r"\bshow me\s+(my|the)\s+(files?|folder|downloads|documents|desktop)\b",
    ],
}

# Compile all patterns once
_COMPILED: dict[str, list[re.Pattern]] = {
    intent: [re.compile(p, re.IGNORECASE) for p in patterns]
    for intent, patterns in INTENTS.items()
}


def classify_intent(text: str, key_phrases: list = None) -> str:
    """
    Classify user text into an intent.

    Args:
        text: Raw user input
        key_phrases: Key phrases from Azure NLP (optional, boosts accuracy)

    Returns:
        Intent string (e.g. "weather_query") or "general_chat"
    """
    combined = text.lower()
    if key_phrases:
        combined += " " + " ".join(key_phrases).lower()

    for intent, patterns in _COMPILED.items():
        for pattern in patterns:
            if pattern.search(combined):
                return intent

    return "general_chat"


# ─────────────────────────────────────────────────────────────
# Intent Router — maps intents to handler functions
# ─────────────────────────────────────────────────────────────
class IntentRouter:
    """
    Routes classified intents to registered handler functions.
    Each handler receives: (text, analysis_result) → returns str reply
    """

    def __init__(self):
        self._handlers: dict[str, Callable] = {}

    def register(self, intent: str, handler: Callable):
        """Register a handler for a given intent."""
        self._handlers[intent] = handler

    def route(self, text: str, analysis: dict) -> tuple[str, str]:
        """
        Route text to the correct handler.

        Returns:
            (intent, reply) tuple
        """
        intent = classify_intent(
            text,
            key_phrases=analysis.get("key_phrases", [])
        )

        handler = self._handlers.get(intent) or self._handlers.get("general_chat")
        if handler:
            reply = handler(text, analysis)
        else:
            reply = "I'm not sure how to help with that yet. I'm always learning."

        return intent, reply
