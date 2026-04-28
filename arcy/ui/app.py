"""
Arcy — pywebview Bridge (Pro Edition)
Exposes session management, deletion, and AI handlers to the JS interface.
"""

import webview
import threading
import os
import json
from pathlib import Path


class ArcyBridge:
    """
    Exposes Python methods to JavaScript via pywebview.
    """

    def __init__(self, arcy_core=None):
        self._core = arcy_core 
        self._window = None     

    def set_window(self, window):
        self._window = window

    # ── Session Bridge ──────────────────────────
    def get_session_index(self):
        """Fetch the session metadata index."""
        from arcy.core.session_manager import load_session_index
        return load_session_index()

    def load_session(self, session_id: str):
        """Switch to a persistent chat session."""
        if self._core:
            from arcy.core.session_manager import load_messages
            messages = load_messages(session_id)
            self._core.switch_session(session_id, messages)
            return messages
        return []

    def delete_session(self, session_id: str):
        """Permanently remove a session."""
        from arcy.core.session_manager import delete_session
        delete_session(session_id)
        return True

    # ── Called by JS: user sends a message ──────────────────────────
    def handle_user_message(self, text: str, session_id: str = None):
        """Python processes the incoming chat text."""
        if self._core:
            # Run in background so UI stays smooth
            threading.Thread(target=self._core.process_text_input, args=(text, session_id), daemon=True).start()
            return "ok"
        return "Thinking..."

    def send_state(self, state: str):
        """state: idle | thinking"""
        if self._window:
            js_state = json.dumps(state)
            self._window.evaluate_js(f"window.arctAPI.setArcyState({js_state})")

    def send_arcy_message(self, text: str):
        """Send Arcy's response to the UI."""
        if self._window:
            js_text = json.dumps(text)
            self._window.evaluate_js(f"window.arctAPI.showArcyReply({js_text})")


def launch_ui(bridge: ArcyBridge = None, on_loaded=None):
    """Launch the Gemini-style chat UI."""
    if bridge is None:
        bridge = ArcyBridge()

    web_dir = Path(__file__).parent / "web"
    index_path = web_dir / "index.html"

    window = webview.create_window(
        title="Arcy — Advanced AI",
        url=str(index_path),
        js_api=bridge,
        width=1200,
        height=800,
        resizable=True,
        background_color="#0a0a0f",
        on_top=False,
    )

    bridge.set_window(window)

    def _on_loaded():
        if on_loaded:
            on_loaded(bridge)

    webview.start(
        _on_loaded,
        gui="qt",
        debug=False,
        private_mode=True,
    )


if __name__ == "__main__":
    launch_ui()
