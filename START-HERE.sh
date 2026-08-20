#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  AI Security Workshop launcher for macOS and Linux.
#
#  Finds a Python 3 and hands over to labs/serve-deck.py, which does the real
#  work. Nothing to install beyond Ollama and Python 3.
#
#  Linux: run  ./START-HERE.sh   (or double-click if your file manager
#  is set to run executables).
#  macOS: double-click "START-HERE.command".
# ---------------------------------------------------------------------------
set -u

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
server="$here/labs/serve-deck.py"

py=""
for candidate in python3 python /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)' >/dev/null 2>&1; then
      py="$candidate"
      break
    fi
  fi
done

if [ -z "$py" ]; then
  echo
  echo "  Python 3 was not found, so the workshop server cannot start."
  echo
  echo "  macOS : run  xcode-select --install   (or install Python from python.org)"
  echo "  Linux : install it with your package manager, e.g."
  echo "            sudo apt install python3      # Debian / Ubuntu"
  echo "            sudo dnf install python3      # Fedora"
  echo
  echo "  The slides themselves work without this - open"
  echo "  slides/ai-fundamentals.html in a browser. Only the live chat needs it."
  echo
  read -r -p "  Press Enter to close " _ || true
  exit 1
fi

exec "$py" -u "$server"
