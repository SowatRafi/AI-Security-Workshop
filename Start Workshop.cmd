@echo off
REM ---------------------------------------------------------------------------
REM  AI SECURITY WORKSHOP - START HERE
REM
REM  Double-click this file. That is the whole setup.
REM
REM  It will:
REM    - start Ollama if it is not already running
REM    - download the open-source model the first time (about 2 GB)
REM    - build AtlasBot, the assistant the students attack
REM    - open the slides in your browser with the live chat working
REM
REM  Needs Ollama installed once, from https://ollama.com/download
REM  Nothing else: no Python, no accounts, no API keys, no admin rights.
REM
REM  Keep the window that opens - closing it stops the workshop server.
REM  Nothing is exposed to the network; everything stays on this machine.
REM ---------------------------------------------------------------------------

title AI Security Workshop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0labs\serve-deck.ps1"

if errorlevel 1 (
  echo.
  echo   Something went wrong above.
  echo.
  pause
)
