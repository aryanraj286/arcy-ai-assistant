"""
Arcy — System Control Connector
Lets Arcy open files, apps, folders, websites, and more.
Works on Windows using os.startfile() and subprocess.

Voice commands handled:
  "open Chrome"
  "open my project file"
  "open Downloads folder"
  "open YouTube"
  "open calculator"
  "open notepad"
"""

import os
import subprocess
import re
import webbrowser
import urllib.parse
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# App shortcuts — common apps the user might say
# Arcy maps voice words → actual executable or known path
# ─────────────────────────────────────────────────────────────
APP_MAP = {
    # Browsers
    "chrome":       r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google":       r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":      r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "browser":      r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    # System apps
    "notepad":      "notepad.exe",
    "calculator":   "calc.exe",
    "paint":        "mspaint.exe",
    "task manager": "taskmgr.exe",
    "settings":     "ms-settings:",
    "control panel":"control.exe",
    "file explorer":"explorer.exe",
    "explorer":     "explorer.exe",

    # Dev tools
    "vs code":      r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vscode":       r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "terminal":     "wt.exe",        # Windows Terminal
    "cmd":          "cmd.exe",
    "powershell":   "powershell.exe",

    # Common apps
    "spotify":      r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
    "discord":      r"C:\Users\{user}\AppData\Local\Discord\Update.exe",
    "whatsapp":     r"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe",
    "telegram":     r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "vlc":          r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "word":         "WINWORD.EXE",
    "excel":        "EXCEL.EXE",
    "powerpoint":   "POWERPNT.EXE",
}

# Website shortcuts
WEBSITE_MAP = {
    "youtube":      "https://www.youtube.com",
    "google":       "https://www.google.com",
    "gmail":        "https://mail.google.com",
    "github":       "https://www.github.com",
    "chatgpt":      "https://www.chat.openai.com",
    "netflix":      "https://www.netflix.com",
    "instagram":    "https://www.instagram.com",
    "twitter":      "https://www.twitter.com",
    "linkedin":     "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
    "maps":         "https://maps.google.com",
    "translate":    "https://translate.google.com",
}

# Folder shortcuts
FOLDER_MAP = {
    "downloads":    str(Path.home() / "Downloads"),
    "documents":    str(Path.home() / "Documents"),
    "desktop":      str(Path.home() / "Desktop"),
    "pictures":     str(Path.home() / "Pictures"),
    "music":        str(Path.home() / "Music"),
    "videos":       str(Path.home() / "Videos"),
    "project":      r"C:\ai_assistant",   # Arcy's own project folder
    "ai assistant": r"C:\ai_assistant",
}


def handle_open_command(text: str) -> str:
    """
    Main handler. Parses the open command and dispatches.

    Args:
        text: Raw user text e.g. "open Chrome" or "open my Downloads folder"

    Returns:
        Natural language reply confirming what was opened (or error)
    """
    text_lower = text.lower().strip()

    # ── 1. Check if it's a URL (user said a URL directly) ──────
    url_match = re.search(r'https?://\S+', text_lower)
    if url_match:
        url = url_match.group()
        return _open_url(url)

    # ── 2. Extract the target after "open" / "launch" / "start" ─
    target = re.sub(
        r'^(open|launch|start|run|show|go to|navigate to|can you open|please open)\s+',
        '', text_lower
    ).strip()

    # Remove filler words
    target = re.sub(r'\b(the|my|a|an)\b', '', target).strip()

    # ── 3. Check website map ────────────────────────────────────
    for keyword, url in WEBSITE_MAP.items():
        if keyword in target:
            return _open_url(url, keyword)

    # ── 4. Check folder map ─────────────────────────────────────
    for keyword, path in FOLDER_MAP.items():
        if keyword in target:
            return _open_path(path, f"{keyword.title()} folder")

    # ── 5. Check app map ────────────────────────────────────────
    user = os.environ.get("USERNAME", "User")
    for keyword, app_path in APP_MAP.items():
        if keyword in target:
            resolved = app_path.replace("{user}", user)
            return _open_app(resolved, keyword.title())

    # ── 6. Try to find a file with that name on the system ──────
    found = _search_for_file(target)
    if found:
        return _open_path(found, target)

    # ── 7. Dynamic Start Menu App Indexer ──────────────────────────
    found_app = _search_start_menu(target)
    if found_app:
        return _open_app(found_app, target.title())

    return (
        f"I couldn't find '{target}' on your PC. "
        f"You can tell me the full path, or I can search the web for it."
    )


def handle_web_search(text: str) -> str:
    """Handles web search queries like 'search on youtube for X'."""
    text_lower = text.lower().strip()
    user = os.environ.get("USERNAME", "User")
    
    # Extract query
    # Remove search verbs and engine/browser names from the start or focused parts
    query = re.sub(r'^(search for|search on|search|find|google|youtube|bing|look up)\s+', '', text_lower).strip()
    query = re.sub(r'\b(on youtube|on google|on bing|on chrome|on edge|in youtube|in google|in bing|in chrome|in edge)\b', '', query).strip()
    
    if not query:
        query = text_lower
        
    encoded_query = urllib.parse.quote(query)
    
    # ─── 1. Determine Search Engine ───────────────────────────
    if "youtube" in text_lower:
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        engine = "YouTube"
    elif "bing" in text_lower:
        url = f"https://www.bing.com/search?q={encoded_query}"
        engine = "Bing"
    else:
        url = f"https://www.google.com/search?q={encoded_query}"
        engine = "Google"
        
    # ─── 2. Determine Browser (if specified) ──────────────────
    browser_exe = None
    browser_name = "your default browser"
    
    if "chrome" in text_lower:
        browser_exe = APP_MAP.get("chrome").replace("{user}", user)
        browser_name = "Chrome"
    elif "edge" in text_lower:
        browser_exe = APP_MAP.get("edge").replace("{user}", user)
        browser_name = "Edge"
        
    try:
        if browser_exe and os.path.exists(browser_exe):
            subprocess.Popen([browser_exe, url])
            return f"Searching {engine} for '{query}' using {browser_name}."
        else:
            webbrowser.open(url)
            return f"Searching {engine} for '{query}' in {browser_name}."
    except Exception as e:
        return f"I couldn't perform the search: {e}"


def _open_url(url: str, name: str = None) -> str:
    """Open a URL in the default browser using python's webbrowser."""
    try:
        webbrowser.open(url)
        label = name.title() if name else url
        return f"Opening {label} in your browser."
    except Exception as e:
        return f"Couldn't open the URL: {e}"


def _search_start_menu(app_name: str) -> str | None:
    """Dynamically searches the Windows Start Menu for an app."""
    paths = [
        Path(os.environ.get("ProgramData", "C:/ProgramData")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("APPDATA", "C:/Users/Default/AppData/Roaming")) / "Microsoft/Windows/Start Menu/Programs"
    ]
    
    clean_name = app_name.lower().replace(" ", "")
    if len(clean_name) < 2:
        return None
        
    best_match = None
    for p in paths:
        if not p.exists(): continue
        for root, dirs, files in os.walk(p):
            for file in files:
                if file.endswith(".lnk") or file.endswith(".exe"):
                    file_clean = file.lower().replace(" ", "").replace(".lnk", "").replace(".exe", "")
                    if clean_name in file_clean:
                        # Prioritize exact sub-matches
                        if clean_name == file_clean:
                            return os.path.join(root, file)
                        if not best_match:
                            best_match = os.path.join(root, file)
    return best_match


def _open_path(path: str, label: str = "") -> str:
    """Open a file or folder using Windows default handler."""
    p = Path(path)
    try:
        if p.exists():
            os.startfile(str(p))
            return f"Opening {label or path} for you."
        else:
            return f"I can't find '{path}'. It may have been moved or deleted."
    except Exception as e:
        return f"Couldn't open '{label}': {e}"


def _open_app(app_path: str, label: str = "") -> str:
    """Launch an application."""
    # First try os.startfile for registered apps
    if not os.path.isabs(app_path) or not app_path.endswith(".exe"):
        try:
            os.startfile(app_path)
            return f"Launching {label}."
        except Exception:
            pass

    # Try subprocess for executables
    p = Path(app_path)
    if p.exists():
        try:
            subprocess.Popen([str(p)], shell=False)
            return f"Launching {label}."
        except Exception as e:
            return f"Couldn't launch {label}: {e}"

    # Try shell execution (for system apps like notepad.exe, calc.exe)
    try:
        subprocess.Popen(app_path, shell=True)
        return f"Launching {label}."
    except Exception as e:
        return f"Couldn't find {label} at the expected location. Is it installed?"


def _search_for_file(filename: str) -> str | None:
    """
    Quick search for a file in common locations.
    Returns path if found, None otherwise.
    """
    search_dirs = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path("C:/ai_assistant"),
    ]
    filename_clean = filename.strip().lower()

    for directory in search_dirs:
        if not directory.exists():
            continue
        for file in directory.iterdir():
            if filename_clean in file.name.lower():
                return str(file)
    return None
