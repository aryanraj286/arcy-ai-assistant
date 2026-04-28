"""
Arcy — Config System
Loads all settings from .env file. Single source of truth for the entire system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (c:\ai_assistant\.env)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ─────────────────────────────────────────
# Azure Language Service
# ─────────────────────────────────────────
AZURE_LANGUAGE_ENDPOINT = os.getenv(
    "AZURE_LANGUAGE_ENDPOINT",
    "https://arctator.cognitiveservices.azure.com/"
)
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY", "")

# ─────────────────────────────────────────
# LLM — Provider-agnostic
# Set LLM_PROVIDER to: openai | gemini | groq | azure_openai
# ─────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")  # For Groq/custom endpoints

# Alias for specific use cases (like Gemini STT)
# This allows using Gemini for transcription even if primary LLM is different
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or (LLM_API_KEY if LLM_PROVIDER == "gemini" else "")

# ─────────────────────────────────────────
# Daily Life Connectors
# ─────────────────────────────────────────
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "New Delhi")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# ─────────────────────────────────────────
# Voice Settings
# ─────────────────────────────────────────
VOICE_RATE = int(os.getenv("VOICE_RATE", "175"))        # Words per minute for TTS
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "0.9"))  # 0.0 to 1.0
VOICE_INDEX = int(os.getenv("VOICE_INDEX", "0"))        # 0 = first system voice

# ─────────────────────────────────────────
# Arcy Personality
# ─────────────────────────────────────────
ARCY_NAME = os.getenv("ARCY_NAME", "Arcy")
USER_NAME = os.getenv("USER_NAME", "")  # Set your name here

# ─────────────────────────────────────────
# UI Settings
# ─────────────────────────────────────────
UI_PORT = int(os.getenv("UI_PORT", "7845"))  # Local server port for UI bridge
UI_ALWAYS_ON_TOP = os.getenv("UI_ALWAYS_ON_TOP", "true").lower() == "true"
