#!/usr/bin/env python3
"""
AI Security Workshop - launcher (macOS, Linux, Windows).

Double-click the launcher for your system; it runs this:
    macOS    Start-Workshop.command
    Linux    start-workshop.sh
    Windows  Start-Workshop.cmd

What this does:
  1. finds Ollama, and starts it if it is not already running
  2. downloads the open-source model (llama3.2) the first time only
  3. builds AtlasBot, the practice assistant the students attack
  4. serves this folder at http://localhost:8000
  5. proxies /ollama/* through to Ollama, so the slides reach the model
     on their OWN origin
  6. opens the deck in your browser

Why step 5 matters. A browser page that fetches http://127.0.0.1:11434 directly
is doing two things browsers now police: a cross-origin request (Ollama refuses
a page opened off disk, which sends "Origin: null"), and a local-network request
(Chrome 138+ gates page->localhost behind a permission prompt). A fetch to a path
on the page's own origin is neither, so it just works - any browser, no Ollama
configuration, no prompt.

Standard library only. Binds to localhost: nothing is exposed to the network.
Stop it with Ctrl+C, or by closing the window.
"""

import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, "labs", "prompt-injection-in-action")
OLLAMA_URL = "http://127.0.0.1:11434"
PORTS = range(8000, 8011)

IS_WIN = sys.platform.startswith("win")
COLOR = (not IS_WIN) or os.environ.get("WT_SESSION") or os.environ.get("TERM")


def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def say(m):   print(f"  {m}", flush=True)
def good(m):  print(f"  {_c('92', '[ok]')}   {m}", flush=True)
def warn(m):  print(f"  {_c('93', '[warn]')} {m}", flush=True)
def bad(m):   print(f"  {_c('91', '[fail]')} {m}", flush=True)


# --------------------------------------------------------------------------
# Ollama
# --------------------------------------------------------------------------

def find_ollama():
    found = shutil.which("ollama")
    if found:
        return found
    guesses = [
        "/usr/local/bin/ollama",
        "/opt/homebrew/bin/ollama",
        "/usr/bin/ollama",
        os.path.expanduser("~/.local/bin/ollama"),
        "/Applications/Ollama.app/Contents/Resources/ollama",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
    ]
    for g in guesses:
        if os.path.isfile(g):
            return g
    return None


def ollama_up(timeout=2):
    try:
        with urllib.request.urlopen(OLLAMA_URL + "/", timeout=timeout):
            return True
    except Exception:
        return False


def wait_for_ollama(seconds):
    for _ in range(seconds):
        if ollama_up():
            return True
        time.sleep(1)
    return False


def start_ollama(exe):
    try:
        if sys.platform == "darwin" and os.path.isdir("/Applications/Ollama.app"):
            subprocess.Popen(["open", "-a", "Ollama"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if IS_WIN:
                kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
            else:
                kwargs["start_new_session"] = True
            subprocess.Popen([exe, "serve"], **kwargs)
    except Exception as e:
        warn(f"Could not start Ollama automatically: {e}")


def run(exe, *args, quiet=True):
    try:
        out = subprocess.run([exe, *args], cwd=LAB, capture_output=True, text=True, timeout=1800)
        return out.returncode == 0, (out.stdout or "") + (out.stderr or "")
    except Exception as e:
        return False, str(e)


def prepare_model():
    """Returns True when atlasbot is ready to talk to."""
    exe = find_ollama()
    if not exe:
        warn("Ollama is not installed - every slide still works, but the live chat will not.")
        say("Install it from https://ollama.com/download, then run this again.")
        return False

    if not ollama_up():
        say("Starting Ollama...")
        start_ollama(exe)
        if not wait_for_ollama(30):
            warn("Ollama did not start - every slide still works, but the live chat will not.")
            return False
    good("Ollama is running")

    ok, listing = run(exe, "list")
    if not ok:
        listing = ""

    if "llama3.2" not in listing:
        say("Downloading the model (llama3.2, about 2 GB). First run only, please wait...")
        try:
            subprocess.run([exe, "pull", "llama3.2"], cwd=LAB, timeout=3600)
        except Exception as e:
            warn(f"Download failed: {e}")
            return False

    if "atlasbot" not in listing:
        say("Building the practice assistant...")
        run(exe, "create", "atlasbot", "-f", "./Modelfile")
        run(exe, "create", "atlasbot-hard", "-f", "./Modelfile.hardened")

    ok, listing = run(exe, "list")
    if ok and "atlasbot" in listing:
        good("AtlasBot is ready")
        return True

    warn("Could not build AtlasBot - see labs/prompt-injection-in-action/README.md")
    return False


# --------------------------------------------------------------------------
# static files + Ollama proxy
# --------------------------------------------------------------------------

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass  # keep the window readable

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self, method):
        target = OLLAMA_URL + self.path[len("/ollama"):]
        data = None
        if method == "POST":
            length = int(self.headers.get("Content-Length") or 0)
            data = self.rfile.read(length) if length else b"{}"
        req = urllib.request.Request(
            target, data=data, method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as up:
                body = up.read()
                self.send_response(up.status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self._send_json(502, {"error": f"Ollama did not answer: {e}"})

    def do_POST(self):
        if self.path.startswith("/ollama/"):
            self._proxy("POST")
        else:
            self.send_error(405)

    def do_GET(self):
        if self.path.startswith("/ollama/"):
            self._proxy("GET")
            return
        if self.path in ("/", ""):
            self.path = "/slides/ai-fundamentals.html"
        super().do_GET()


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    print(flush=True)
    print("  " + _c("96", "AI Security Workshop"), flush=True)
    print("  " + _c("96", "===================="), flush=True)

    ready = prepare_model()

    httpd = None
    for port in PORTS:
        try:
            httpd = Server(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if httpd is None:
        bad(f"Could not open a port in {PORTS.start}-{PORTS.stop - 1}.")
        input("  Press Enter to close ")
        return 1

    port = httpd.server_address[1]
    deck = f"http://localhost:{port}/slides/ai-fundamentals.html"

    print(flush=True)
    good(f"Serving {ROOT}")
    say(f"Deck: {deck}")
    if not ready:
        warn("Live chat is unavailable, but every slide still works.")
    print(flush=True)
    print("  " + _c("93", "Keep this window open while you present. Closing it stops the server."), flush=True)
    print(flush=True)

    threading.Timer(1.0, lambda: webbrowser.open(deck)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        say("Stopped.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
