"""
Arcy — Main Orchestrator (Pro Edition)
Coordinates Sessions, Long-term Memory, and Internet Search.
"""

import threading
import re
from datetime import datetime

from arcy.core.config import ARCY_NAME, USER_NAME
from arcy.core.greeting import get_startup_message
from arcy.core.memory import ConversationMemory
from arcy.nlp.analyzer import analyze
from arcy.nlp.intent_router import IntentRouter
from arcy.ai.reply_engine import generate_reply
from arcy.connectors.weather import get_weather
from arcy.connectors.news import get_top_headlines
from arcy.connectors.system_control import handle_open_command
from arcy.reminders.reminder_engine import (
    add_reminder, list_reminders, get_due_reminders,
    extract_reminder_from_text
)
from arcy.core.session_manager import save_session


class ArcyCore:
    """
    Central orchestrator for the Advanced Arcy experience.
    """

    def __init__(self):
        self.memory   = ConversationMemory(max_turns=20)
        self.router   = IntentRouter()
        self.bridge   = None
        self.current_session_id = None

        # Register intent handlers
        self._register_handlers()
        
        print(f"[{ARCY_NAME}] Pro Core initialized.")

    def startup(self):
        """Run startup sequence: greet the user."""
        due = [r["text"] for r in get_due_reminders()]
        greeting = get_startup_message(due_reminders=due)
        self._respond(greeting)

    def process_text_input(self, text: str, session_id: str = None) -> str:
        """
        Full pipeline: text + history → analyze → route → persist → reply.
        """
        self.current_session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        print(f"[{ARCY_NAME}] Input: {text} (Session: {self.current_session_id})")
        
        self._set_ui_state("thinking")

        # Step 1: Recall Long-term Context from ChromaDB
        historical_context = self.memory.query_long_term(text)

        # Step 2: NLP Analysis
        analysis = analyze(text)

        # Step 3: Route to handler
        intent, reply = self.router.route(text, analysis)

        # If it's a general chat, we use the LLM with full context
        if intent == "general_chat":
            reply = generate_reply(
                text, 
                sentiment=analysis.get("sentiment", "neutral"),
                conversation_history=self.memory.to_messages(),
                history_context=historical_context
            )

        # Step 4: Store in memory (Memory handles its own ChromaDB sync)
        self.memory.add_user(text)
        self.memory.add_assistant(reply)

        # Step 5: Save Session to JSON Disk
        # Generate title only if session is new/empty
        title = None
        if len(self.memory) <= 2: # First exchange
            title = self._generate_title(text)
        
        save_session(self.current_session_id, self.memory.to_messages(), title=title)

        # Step 6: Display + update UI
        self._respond(reply)
        return reply

    def switch_session(self, session_id: str, messages: list):
        """Switch the current working memory to a past session."""
        print(f"[{ARCY_NAME}] Switching to session: {session_id}")
        self.current_session_id = session_id
        self.memory.load_from_list(messages)

    def _respond(self, text: str):
        """Standard channel to send Arcy's output to the UI."""
        if self.bridge:
            self.bridge.send_arcy_message(text)
        self._set_ui_state("idle")

    def _set_ui_state(self, state: str):
        if self.bridge:
            self.bridge.send_state(state)

    def _generate_title(self, text: str):
        """Simple heuristic for chat titles."""
        clean = re.sub(r'[^\w\s]', '', text)
        words = clean.split()
        title = " ".join(words[:5])
        return (title[:30] + "...") if len(title) > 30 else title

    def _register_handlers(self):
        """Register all router intent handlers."""
        r = self.router
        r.register("weather_query", self._handle_weather)
        r.register("news_query", self._handle_news)
        r.register("set_reminder", self._handle_set_reminder)
        r.register("list_reminders", self._handle_list_reminders)
        r.register("clear_reminders", self._handle_clear_reminders)
        r.register("time_query", self._handle_time)
        r.register("date_query", self._handle_date)
        r.register("daily_plan", self._handle_daily_plan)
        r.register("emotional_support", self._handle_emotional_support)
        r.register("self_query", self._handle_self_query)
        r.register("greet_arcy", self._handle_greet)
        r.register("open_command", self._handle_open_command)
        r.register("web_search", self._handle_web_search)
        r.register("general_chat", self._handle_general_chat)

    # ─────────────────────────────────────────────────────────
    # Handler Implementations
    # ─────────────────────────────────────────────────────────
    def _handle_weather(self, text, analysis): 
        city = None
        for e in analysis.get("entities", []):
            if e["category"] in ("Location", "GPE"): city = e["text"]; break
        return get_weather(city)

    def _handle_news(self, text, analysis):
        topic = None
        phrases = analysis.get("key_phrases", [])
        for p in phrases:
            if p.lower() not in {"news", "headlines", "latest"}: topic = p; break
        return get_top_headlines(topic)

    def _handle_set_reminder(self, text, analysis):
        r, t = extract_reminder_from_text(text)
        return add_reminder(r, t)

    def _handle_list_reminders(self, text, analysis): return list_reminders()
    def _handle_clear_reminders(self, text, analysis):
        from arcy.reminders.reminder_engine import clear_all_reminders
        return clear_all_reminders()

    def _handle_time(self, text, analysis): return f"It's {datetime.now().strftime('%I:%M %p')}."
    def _handle_date(self, text, analysis): return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."
    def _handle_daily_plan(self, text, analysis): return f"Here is your plan, Sir. {list_reminders()}"

    def _handle_emotional_support(self, text, analysis):
        return generate_reply(text, sentiment="negative", conversation_history=self.memory.to_messages())

    def _handle_open_command(self, text, analysis): return handle_open_command(text)
    
    def _handle_web_search(self, text, analysis):
        from arcy.connectors.web_search import web_search
        return web_search(text)

    def _handle_self_query(self, text, analysis):
        return f"I'm {ARCY_NAME}, your personal AI companion. Currently optimized with history tracking and web-search capabilities."

    def _handle_greet(self, text, analysis): return get_startup_message()

    def _handle_general_chat(self, text, analysis):
        return generate_reply(text, sentiment="neutral", conversation_history=self.memory.to_messages())
