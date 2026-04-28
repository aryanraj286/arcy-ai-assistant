"""
DataManager — Arcy's Permanent Ledger
Handles local JSON storage for user profile, and facts.
"""

import json
import os
from pathlib import Path

# Data directory
DATA_DIR = Path("data")
PROFILE_FILE = DATA_DIR / "profile.json"

def ensure_data_dir():
    """Ensure the data folder exists."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_profile(data: dict):
    """Save user profile facts."""
    ensure_data_dir()
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_profile() -> dict:
    """Load user profile facts."""
    if not PROFILE_FILE.exists():
        return {}
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def update_fact(key: str, value: str):
    """Save a specific fact about the user."""
    profile = load_profile()
    profile[key] = value
    save_profile(profile)

def get_fact(key: str, default=None):
    """Get a specific fact about the user."""
    profile = load_profile()
    return profile.get(key, default)
