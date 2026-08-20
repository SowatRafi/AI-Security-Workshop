@echo off
REM ---------------------------------------------------------------------------
REM  AI SECURITY WORKSHOP - START HERE  (Windows)
REM
REM  Double-click this file. That is the whole setup.
REM
REM  It starts Ollama, downloads the open-source model the first time, builds
REM  the practice assistant, and opens the slides with the live chat working.
REM
REM  Needs Ollama installed once, from https://ollama.com/download
REM  Nothing else: no accounts, no API keys, no admin rights.
REM
REM  Keep the window that opens - closing it stops the workshop server.
REM  Nothing is exposed to the network; everything stays on this machine.
REM ---------------------------------------------------------------------------

title AI Security Workshop
cd /d "%~dp0"

REM Prefer Python so every platform behaves identically; fall back to
REM PowerShell, which every Windows machine already has.
where py >nul 2>nul && (py -3 -u "labs\serve-deck.py" & goto :done)
where python >nul 2>nul && (python -u "labs\serve-deck.py" & goto :done)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "labs\serve-deck.ps1"

:done
if errorlevel 1 (
  echo.
  echo   Something went wrong above.
  echo.
  pause
)
