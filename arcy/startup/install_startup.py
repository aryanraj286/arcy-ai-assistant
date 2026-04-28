"""
Arcy — Windows Auto-Start Installer
Registers Arcy with Windows Task Scheduler to run at login.
Run: python -m arcy.startup.install_startup
"""

import subprocess
import sys
from pathlib import Path


def install_startup():
    """Register Arcy to auto-start when the user logs into Windows."""
    python_exe = sys.executable
    main_script = Path(__file__).parent.parent.parent / "main.py"
    task_name = "ArcyAICompanion"

    # Build the schtasks command
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", f'"{python_exe}" "{main_script}"',
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F",   # Force overwrite if already exists
    ]

    print(f"[Arcy Startup] Registering task: {task_name}")
    print(f"  Python: {python_exe}")
    print(f"  Script: {main_script}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[Arcy Startup] ✅ Auto-start registered successfully!")
            print("  Arcy will now start automatically when you log into Windows.")
        else:
            print(f"[Arcy Startup] ❌ Failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Arcy Startup] ❌ Error: {e}")


def uninstall_startup():
    """Remove Arcy from Windows startup."""
    task_name = "ArcyAICompanion"
    cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[Arcy Startup] ✅ Auto-start removed.")
        else:
            print(f"[Arcy Startup] ❌ Failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Arcy Startup] ❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()

    if args.uninstall:
        uninstall_startup()
    else:
        install_startup()
