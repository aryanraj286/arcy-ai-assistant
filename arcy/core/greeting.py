"""
Arcy — Time-based Greeting & Daily Brief
Generates personalized greetings and morning briefings.
"""

import random
from datetime import datetime
from arcy.core.config import ARCY_NAME


def get_time_greeting() -> str:
    """Returns a time-appropriate greeting, addressing the user as Sir."""
    hour = datetime.now().hour
    
    # Jarvis-style dynamic phrases
    morning_phrases = [
        "Good morning, Sir. Systems online and ready for your command.",
        "Good morning, Sir. I hope you're feeling refreshed today.",
        "Rise and shine, Sir. The world awaits your brilliance.",
        "Top of the morning to you, Sir. How can I assist you today?"
    ]
    
    afternoon_phrases = [
        "Good afternoon, Sir. I'm standing by whenever you need me.",
        "Good afternoon, Sir. Is there anything I can help you with today?",
        "Good afternoon, Sir. The day is progressing nicely. What's on the agenda?",
        "Good afternoon, Sir. Always a pleasure to be of service."
    ]
    
    evening_phrases = [
        "Good evening, Sir. How was your day?",
        "Good evening, Sir. It's a fine time for reflection, or perhaps a new project?",
        "Good evening, Sir. I'm here if you need any assistance before you wrap up.",
        "Good evening, Sir. The day may be ending, but I'm still at your disposal."
    ]
    
    night_phrases = [
        "Working late, Sir? I'm here. Don't forget to rest.",
        "The stars are out, Sir. Burning the midnight oil again?",
        "Late hours are often the most productive, Sir. I'm right here with you.",
        "Good night, Sir. Well, for those of us who don't sleep, anyway."
    ]

    if 5 <= hour < 12:
        return random.choice(morning_phrases)
    elif 12 <= hour < 17:
        return random.choice(afternoon_phrases)
    elif 17 <= hour < 21:
        return random.choice(evening_phrases)
    else:
        return random.choice(night_phrases)


def get_startup_message(due_reminders: list = None) -> str:
    """
    Generates the startup greeting, optionally including due reminders.
    """
    greeting = get_time_greeting()

    if not due_reminders:
        return greeting

    if len(due_reminders) == 1:
        return f"{greeting} By the way, Sir, you have one reminder: {due_reminders[0]}"
    else:
        count = len(due_reminders)
        return f"{greeting} You have {count} reminders waiting, Sir. Shall I go through them?"
