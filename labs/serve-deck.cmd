@echo off
REM ---------------------------------------------------------------------------
REM  Serve the slide decks over http://localhost so the live chat on slides
REM  16-17 can reach Ollama.
REM
REM  Why this exists: Ollama allows browser calls from http://localhost and
REM  http://127.0.0.1 out of the box, but refuses them from a file:// page
REM  (the browser sends "Origin: null", which is not on Ollama's allow-list).
REM  Serving the deck locally therefore needs no Ollama configuration at all.
REM
REM  Double-click this file, then open:  http://localhost:8000/slides/ai-fundamentals.html
REM  Close the window, or press Ctrl+C, to stop serving.
REM
REM  Nothing leaves this machine: the server binds to localhost only.
REM ---------------------------------------------------------------------------

cd /d "%~dp0.."

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo   Python was not found on PATH, so this launcher cannot start a server.
  echo.
  echo   Either install Python, or open the deck straight from the file
  echo   and set OLLAMA_ORIGINS=* instead - see
  echo   labs\prompt-injection-in-action\README.md, "Live chat setup".
  echo.
  pause
  exit /b 1
)

echo.
echo   Serving this folder at http://localhost:8000
echo.
echo   Open:  http://localhost:8000/slides/ai-fundamentals.html
echo.
echo   Press Ctrl+C to stop.
echo.

python -m http.server 8000 --bind 127.0.0.1
