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


MODEL = "llama3.2"
MODEL_DESC = "Meta's Llama 3.2 (3B parameters), about 2.0 GB"
DOWNLOAD_PAGE = "https://ollama.com/download"
LINUX_INSTALL = "curl -fsSL https://ollama.com/install.sh | sh"


def ask_yes_no(question, default_yes=True):
    """Ask permission. Never assume yes when there is nobody to answer."""
    suffix = "[Y/n]" if default_yes else "[y/N]"
    if not sys.stdin or not sys.stdin.isatty():
        say(f"{question} {suffix}")
        warn("No console to answer on - assuming no. Run the launcher by double-clicking it.")
        return False
    try:
        answer = input(f"  {question} {suffix} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(flush=True)
        return False
    if not answer:
        return default_yes
    return answer in ("y", "yes")


def offer_ollama_install():
    """Ollama is missing. Explain, ask, and only then do anything."""
    print(flush=True)
    warn("Ollama is not installed - and the live chat needs it.")
    print(flush=True)
    say("Ollama is the free, open-source runner that hosts the model on this")
    say("machine. Nothing you type in the workshop ever leaves your computer.")
    print(flush=True)

    if sys.platform.startswith("linux"):
        say("It can be installed with Ollama's own official installer:")
        say(f"    {_c('96', LINUX_INSTALL)}")
        print(flush=True)
        if ask_yes_no("Run that now?", default_yes=False):
            say("Installing - you may be asked for your password...")
            try:
                subprocess.run(LINUX_INSTALL, shell=True, timeout=1800)
            except Exception as e:
                bad(f"Install failed: {e}")
                return False
            if find_ollama():
                good("Ollama installed")
                return True
            bad("Ollama still not found - install it yourself and run this again.")
            return False
        say(f"Skipped. You can install it later from {DOWNLOAD_PAGE}")
        return False

    say(f"Download it from  {_c('96', DOWNLOAD_PAGE)}")
    print(flush=True)
    if ask_yes_no("Open that page in your browser now?"):
        webbrowser.open(DOWNLOAD_PAGE)
        say("Install Ollama, then run this launcher again.")
    else:
        say("No problem - install it whenever you like, then run this again.")
    return False


def offer_model_download(exe):
    """The 2 GB download. Always ask first."""
    print(flush=True)
    warn(f"The model is not downloaded yet.")
    print(flush=True)
    say(f"The live chat needs one open-source model:")
    say(f"    {_c('96', MODEL)}  -  {MODEL_DESC}")
    say("It downloads once, then runs entirely offline on this machine.")
    print(flush=True)
    if not ask_yes_no("Download it now?"):
        say("Skipped. Every slide still works - only the live chat needs the model.")
        return False
    say("Downloading. This is the slow part, and it only happens once...")
    try:
        result = subprocess.run([exe, "pull", MODEL], cwd=LAB, timeout=7200)
    except Exception as e:
        bad(f"Download failed: {e}")
        return False
    if result.returncode != 0:
        bad("Download failed - check your internet connection and run this again.")
        return False
    good("Model downloaded")
    return True


def prepare_model():
    """Check what is present, ask before downloading anything, then set up."""
    print(flush=True)
    say("Checking what you have...")
    print(flush=True)

    exe = find_ollama()
    if not exe:
        offer_ollama_install()
        exe = find_ollama()
        if not exe:
            print(flush=True)
            warn("Continuing without the live chat. Every slide still works.")
            return False
    good("Ollama is installed")

    if not ollama_up():
        say("Starting Ollama...")
        start_ollama(exe)
        if not wait_for_ollama(30):
            warn("Ollama would not start - every slide still works, but the live chat will not.")
            say(f"Try starting Ollama yourself, then run this again.")
            return False
    good("Ollama is running")

    ok, listing = run(exe, "list")
    if not ok:
        listing = ""

    if MODEL not in listing:
        if not offer_model_download(exe):
            return False
    else:
        good(f"Model {MODEL} is downloaded")

    if "atlasbot" not in listing:
        say("Building AtlasBot, the practice assistant...")
        ok1, _ = run(exe, "create", "atlasbot", "-f", "./Modelfile")
        run(exe, "create", "atlasbot-hard", "-f", "./Modelfile.hardened")
        if not ok1:
            warn("Could not build AtlasBot - see labs/prompt-injection-in-action/README.md")
            return False

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
