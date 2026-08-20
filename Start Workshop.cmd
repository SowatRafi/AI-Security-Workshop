@echo off
REM ---------------------------------------------------------------------------
REM  AI Security Workshop - start here.
REM
REM  Double-click this file. It serves the workshop folder at
REM  http://localhost:8000 and opens the main deck in your browser.
REM
REM  Why not just open the HTML? Because the live chat on slides 16-17 talks to
REM  Ollama, and Ollama refuses browser calls from a page opened straight off
REM  disk. Served from localhost it works with no Ollama configuration at all.
REM
REM  The slides themselves work fine either way - this is only needed for the
REM  live chat. Nothing is exposed to the network; the server binds to localhost.
REM
REM  Keep the window that opens. Closing it stops the server.
REM ---------------------------------------------------------------------------

title AI Security Workshop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0labs\serve-deck.ps1"

if errorlevel 1 (
  echo.
  echo   The server stopped unexpectedly.
  echo.
  pause
)
