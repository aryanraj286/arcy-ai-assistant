"""
Arcy — Main Entry Point
Run this file to launch Arcy.

Usage:
    python main.py                   # Full launch (UI + voice + AI)
    python main.py --ui-only         # Launch UI only (no voice)
    python main.py --text-only       # Terminal mode (no UI, no voice)
"""

import sys
import argparse
import threading


def main():
    parser = argparse.ArgumentParser(description="Arcy — Personal AI Companion")
    parser.add_argument("--ui-only",    action="store_true", help="Launch UI without voice/AI")
    parser.add_argument("--text-only",  action="store_true", help="Terminal chat mode")
    parser.add_argument("--no-voice",   action="store_true", help="Disable microphone input")
    args = parser.parse_args()

    # ── Terminal / text-only mode ────────────────────────────────
    if args.text_only:
        _run_terminal_mode()
        return

    # ── UI-only demo mode ────────────────────────────────────────
    if args.ui_only:
        from arcy.ui.app import launch_ui
        print("[Arcy] Launching UI in demo mode...")
        launch_ui()
        return

    # ── Full launch: Core + UI ──────────────────────────────────
    from arcy.core.arcy import ArcyCore
    from arcy.ui.app import ArcyBridge, launch_ui

    core   = ArcyCore()
    bridge = ArcyBridge(arcy_core=core)
    core.bridge = bridge

    def on_ui_loaded(b: ArcyBridge):
        """Called when the window is ready — start AI systems."""
        print("[Arcy] UI loaded. Starting systems...")

        # Run startup greeting on a background thread
        # (UI is on main thread via pywebview)
        def _startup():
            core.startup()

        threading.Thread(target=_startup, daemon=True).start()

    print("[Arcy] Launching JARVIS interface...")
    launch_ui(bridge=bridge, on_loaded=on_ui_loaded)


def _run_terminal_mode():
    """Pure terminal chat loop — no UI, no voice."""
    from arcy.core.arcy import ArcyCore
    from arcy.core.greeting import get_startup_message

    core = ArcyCore()
    greeting = get_startup_message()
    print(f"\n{'='*50}")
    print(f"  Arcy — Terminal Mode")
    print(f"{'='*50}")
    print(f"\nArcy: {greeting}")
    print("(Type 'quit' to exit)\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "bye"):
                print("Arcy: Goodbye. I'll be here when you need me.")
                break
            reply = core.process_text_input(user_input)
            print(f"\nArcy: {reply}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nArcy: Goodbye.")
            break


if __name__ == "__main__":
    main()
