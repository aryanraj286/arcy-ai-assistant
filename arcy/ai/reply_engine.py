"""
Arcy — LLM Reply Engine (Provider-Agnostic)
Updated to support Long-term Historical Context (ChromaDB).
"""

import os
from arcy.core.config import (
    LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL,
    ARCY_NAME, USER_NAME
)

# ─────────────────────────────────────────────────────────
# Arcy's core personality — the soul of the assistant
# ─────────────────────────────────────────────────────────
ARCY_SYSTEM_PROMPT = f"""You are {ARCY_NAME}, a highly intelligent and deeply personal AI assistant.
You are inspired by JARVIS from Iron Man — always available, context-aware, calm, and impeccably professional.

Your personality:
- You speak naturally, warmly, and intelligently — never robotic.
- You ALWAYS address the user as "Sir" (unless specifically asked otherwise).
- You are loyal, efficient, and proactive.
- You give concise, actionable responses.
- You refer to yourself as {ARCY_NAME}.

Long-term Memory:
- You have access to [Historical Context] which contains snippets from past conversations. Use them to show you remember the user.
- If the user asks about something they said yesterday or in another chat, check the context provided.
"""


def generate_reply(
    user_text: str,
    sentiment: str = "neutral",
    key_phrases: list = None,
    conversation_history: list = None,
    image_path: str = None,
    history_context: str = ""
) -> str:
    """
    Generate an AI reply from any configured LLM provider.
    """
    if key_phrases is None:
        key_phrases = []
    if conversation_history is None:
        conversation_history = []

    # Enrich the user prompt with NLP context and Long-term history
    enriched_prompt = user_text
    
    if history_context:
        enriched_prompt = f"{history_context}\n\n[Current User Query]: {user_text}"
    
    if key_phrases or sentiment != "neutral":
        context_note = f"\n[System note: User emotion is {sentiment}."
        if key_phrases:
            context_note += f" Key topics: {', '.join(key_phrases[:5])}."
        context_note += " Respond accordingly.]"
        enriched_prompt += context_note

    # Build message history for context
    messages = [{"role": "system", "content": ARCY_SYSTEM_PROMPT}]
    messages.extend(conversation_history[-10:])  # Keep last 10 exchanges
    
    provider = LLM_PROVIDER.lower()

    if not LLM_API_KEY:
        return f"I'm here, Sir, but my thinking engine isn't connected yet. Please add your API key."

    try:
        # ─── OpenAI / Groq / Any OpenAI-compatible API ────────
        if provider in ("openai", "groq", "azure_openai", "openai_compatible"):
            from openai import OpenAI

            client_kwargs = {"api_key": LLM_API_KEY}
            if LLM_BASE_URL:
                client_kwargs["base_url"] = LLM_BASE_URL

            client = OpenAI(**client_kwargs)

            user_msg = {"role": "user", "content": enriched_prompt}
            messages.append(user_msg)

            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.75,
                max_tokens=500,
            )
            return response.choices[0].message.content

        # ─── Google Gemini ────────────────────────────────────
        elif provider == "gemini":
            import requests
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL or 'gemini-1.5-flash'}:generateContent?key={LLM_API_KEY}"
            
            contents = []
            # Historical context (Short-term)
            for msg in conversation_history[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                
            # Current turn parts (includes Long-term history if present)
            contents.append({"role": "user", "parts": [{"text": enriched_prompt}]})
            
            payload = {
                "system_instruction": {"parts": [{"text": ARCY_SYSTEM_PROMPT}]},
                "contents": contents
            }
            
            r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            if r.status_code != 200:
                raise Exception(f"API HTTP {r.status_code}: {r.text[:200]}")
                
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        else:
            return f"Unknown LLM provider: '{provider}'."

    except Exception as e:
        return f"Something went wrong with my thinking engine: {str(e)}"
