#!/usr/bin/env python3
"""
Undo the browser-access setting the workshop launcher offered to add.

The launcher can set OLLAMA_ORIGINS=* so the slides work when opened straight
off disk. That also lets any web page you visit talk to your local Ollama, so
it is worth removing once the workshop is over. This puts Ollama back to how it
shipped.

Run it:
    python3 labs/undo-access.py          (macOS / Linux)
    py -3 labs/undo-access.py            (Windows)

The workshop models are left alone. Remove those with:
    ollama rm nora nora-hard
"""

import subprocess
import sys
import time
import urllib.request

IS_WIN = sys.platform.startswith("win")


def still_open():
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", method="OPTIONS")
    req.add_header("Origin", "null")
    req.add_header("Access-Control-Request-Method", "POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status in (200, 204)
    except Exception:
        return False


def main():
    print("\n  Undoing the workshop's browser-access setting\n")

    if IS_WIN:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "[Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS',$null,'User')"],
                       capture_output=True, timeout=60)
        subprocess.run(["taskkill", "/F", "/IM", "ollama app.exe"], capture_output=True, timeout=30)
        subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], capture_output=True, timeout=30)
    else:
        if sys.platform == "darwin":
            subprocess.run(["launchctl", "unsetenv", "OLLAMA_ORIGINS"], capture_output=True, timeout=60)
        subprocess.run(["pkill", "-f", "ollama"], capture_output=True, timeout=30)

    print("  Removed OLLAMA_ORIGINS and stopped Ollama.")
    print("  Start Ollama again the way you normally do.\n")
    time.sleep(2)

    if still_open():
        print("  Note: Ollama is still accepting calls from file:// pages.")
        print("  It may not have restarted yet - check again once it has.\n")
    else:
        print("  Ollama is back to its default, which refuses those calls.\n")
    print("  The live chat still works through the workshop launcher.\n")


if __name__ == "__main__":
    main()
