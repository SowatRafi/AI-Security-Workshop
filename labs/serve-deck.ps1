# ---------------------------------------------------------------------------
#  Serves the workshop folder at http://localhost:8000 and opens the main deck.
#
#  Why this exists: the in-slide chat on Deck B slides 16-17 calls Ollama from
#  the browser. Ollama accepts calls from http://localhost out of the box, but
#  refuses them from a page opened straight off disk (a file:// page sends
#  "Origin: null", which is not on Ollama's allow-list, so it answers 403).
#  Serving the folder locally sidesteps that with no Ollama configuration.
#
#  Uses only what ships with Windows - no Python, no install, no admin rights.
#  Binds to localhost only: nothing is exposed to the network.
#
#  Stop it by closing the window, or pressing Ctrl+C.
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$port = 8000
$deck = "http://localhost:$port/slides/ai-fundamentals.html"

$mime = @{
  '.html' = 'text/html; charset=utf-8'
  '.htm'  = 'text/html; charset=utf-8'
  '.css'  = 'text/css; charset=utf-8'
  '.js'   = 'text/javascript; charset=utf-8'
  '.json' = 'application/json; charset=utf-8'
  '.md'   = 'text/plain; charset=utf-8'
  '.svg'  = 'image/svg+xml'
  '.png'  = 'image/png'
  '.jpg'  = 'image/jpeg'
  '.gif'  = 'image/gif'
  '.ico'  = 'image/x-icon'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
try {
  $listener.Start()
} catch {
  Write-Host ''
  Write-Host "  Could not open port $port - something else is probably using it." -ForegroundColor Red
  Write-Host "  Close whatever is on port $port and run this again."
  Write-Host ''
  Read-Host '  Press Enter to close'
  exit 1
}

Write-Host ''
Write-Host '  AI Security Workshop' -ForegroundColor Cyan
Write-Host '  --------------------'
Write-Host "  Serving : $root"
Write-Host "  Deck    : $deck"
Write-Host ''
Write-Host '  Your browser should open by itself. Keep this window open while you' -ForegroundColor Yellow
Write-Host '  present - closing it stops the server.' -ForegroundColor Yellow
Write-Host ''

Start-Process $deck

try {
  while ($listener.IsListening) {
    $context  = $listener.GetContext()
    $request  = $context.Request
    $response = $context.Response

    $rel = [System.Uri]::UnescapeDataString($request.Url.AbsolutePath).TrimStart('/')
    if ([string]::IsNullOrWhiteSpace($rel)) { $rel = 'slides/ai-fundamentals.html' }
    $rel = $rel -replace '/', '\'

    $path = Join-Path $root $rel
    $full = [System.IO.Path]::GetFullPath($path)

    # never serve anything outside the workshop folder
    if (-not $full.StartsWith([System.IO.Path]::GetFullPath($root), [System.StringComparison]::OrdinalIgnoreCase)) {
      $response.StatusCode = 403
      $response.Close()
      continue
    }

    if (Test-Path -LiteralPath $full -PathType Leaf) {
      $ext = [System.IO.Path]::GetExtension($full).ToLowerInvariant()
      $type = $mime[$ext]
      if (-not $type) { $type = 'application/octet-stream' }
      $bytes = [System.IO.File]::ReadAllBytes($full)
      $response.ContentType = $type
      $response.ContentLength64 = $bytes.Length
      $response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $msg = [System.Text.Encoding]::UTF8.GetBytes("Not found: $rel")
      $response.StatusCode = 404
      $response.ContentType = 'text/plain; charset=utf-8'
      $response.OutputStream.Write($msg, 0, $msg.Length)
    }
    $response.Close()
  }
} finally {
  $listener.Stop()
  $listener.Close()
}
