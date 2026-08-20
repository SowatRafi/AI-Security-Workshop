#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  AI SECURITY WORKSHOP - START HERE  (macOS)
#
#  Double-click this file. That is the whole setup.
#
#  It starts Ollama, downloads the open-source model the first time, builds the
#  practice assistant, and opens the slides with the live chat working.
#
#  Needs Ollama installed once, from https://ollama.com/download
#  Nothing else: no accounts, no API keys, no admin rights.
#
#  Keep the Terminal window open - closing it stops the workshop server.
#  Nothing is exposed to the network; everything stays on this machine.
#
#  If macOS refuses to open this ("unidentified developer" or no permission),
#  right-click it and choose Open, or run in Terminal:
#      chmod +x "Start-Workshop.command"
# ---------------------------------------------------------------------------
cd "$(dirname "$0")" || exit 1
exec bash "labs/start-workshop.sh"
