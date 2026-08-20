# ---------------------------------------------------------------------------
#  AI Security Workshop - launcher.
#
#  Double-click "Start-Workshop.cmd" in the folder above; it runs this.
#
#  What this does:
#    1. finds Ollama and starts it if it is not already running
#    2. downloads the open-source model (llama3.2) the first time only
#    3. builds AtlasBot, the practice assistant the students attack
#    4. serves this folder at http://localhost:8000
#    5. proxies /ollama/* through to Ollama, so the slides talk to the model
#       on their OWN origin
#    6. opens the deck in your browser
#
#  Why the proxy in step 5 matters. A browser page that fetches
#  http://127.0.0.1:11434 directly is doing two things browsers now police:
#  a cross-origin request (blocked unless Ollama allow-lists the origin) and a
#  local-network request (Chrome 138+ gates this behind a permission prompt, and
#  a page opened straight off disk cannot reliably get through it). Fetching a
#  path on the page's own origin is neither of those, so it just works - in any
#  browser, with no Ollama configuration and no permission prompt.
#
#  Uses only what ships with Windows. Binds to localhost: nothing is exposed
#  to the network. Close the window, or press Ctrl+C, to stop.
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$root    = Split-Path -Parent $PSScriptRoot
$lab     = Join-Path $root 'labs\prompt-injection-in-action'
$port    = 8000
$ollamaU = 'http://127.0.0.1:11434'
$deck    = "http://localhost:$port/slides/ai-fundamentals.html"

function Say  ($m) { Write-Host "  $m" }
function Good ($m) { Write-Host "  [ok]   $m" -ForegroundColor Green }
function Warn ($m) { Write-Host "  [warn] $m" -ForegroundColor Yellow }
function Bad  ($m) { Write-Host "  [fail] $m" -ForegroundColor Red }

Write-Host ''
Write-Host '  AI Security Workshop' -ForegroundColor Cyan
Write-Host '  ====================' -ForegroundColor Cyan

# --- Ollama ----------------------------------------------------------------
$ollama = (Get-Command ollama -ErrorAction SilentlyContinue).Source
if (-not $ollama) {
  $guess = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if (Test-Path $guess) { $ollama = $guess }
}

$modelReady = $false
if (-not $ollama) {
  Warn 'Ollama is not installed - the slides will work, but the live chat will not.'
  Say  'Install it from https://ollama.com/download and run this again.'
} else {
  $appExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
  function Wait-ForOllama ($seconds) {
    for ($i = 0; $i -lt $seconds; $i++) {
      try { Invoke-WebRequest "$ollamaU/" -TimeoutSec 2 -UseBasicParsing | Out-Null; return $true }
      catch { Start-Sleep -Seconds 1 }
    }
    return $false
  }

  if (-not (Wait-ForOllama 2)) {
    Say 'Starting Ollama...'
    if (Test-Path $appExe) { Start-Process $appExe } else { Start-Process $ollama -ArgumentList 'serve' -WindowStyle Hidden }
    [void](Wait-ForOllama 30)
  }

  if (Wait-ForOllama 2) {
    Good 'Ollama is running'
    $have = (& $ollama list 2>$null) -join "`n"

    if ($have -notmatch 'llama3\.2') {
      Say 'Downloading the model (llama3.2, about 2 GB). First run only...'
      & $ollama pull llama3.2 | Out-Host
    }

    if ($have -notmatch 'atlasbot') {
      Say 'Building the practice assistant...'
      Push-Location $lab
      & $ollama create atlasbot      -f ./Modelfile          | Out-Null
      & $ollama create atlasbot-hard -f ./Modelfile.hardened | Out-Null
      Pop-Location
    }

    $check = (& $ollama list 2>$null) -join "`n"
    if ($check -match 'atlasbot') { $modelReady = $true; Good 'AtlasBot is ready' }
    else { Warn 'Could not build AtlasBot - see labs\prompt-injection-in-action\README.md' }
  } else {
    Warn 'Ollama did not start - the slides work, but the live chat will not.'
  }
}

# --- static + proxy server -------------------------------------------------
$mime = @{
  '.html'='text/html; charset=utf-8'; '.htm'='text/html; charset=utf-8'
  '.css'='text/css; charset=utf-8';   '.js'='text/javascript; charset=utf-8'
  '.json'='application/json; charset=utf-8'; '.md'='text/plain; charset=utf-8'
  '.svg'='image/svg+xml'; '.png'='image/png'; '.jpg'='image/jpeg'
  '.gif'='image/gif'; '.ico'='image/x-icon'; '.cmd'='text/plain; charset=utf-8'
  '.ps1'='text/plain; charset=utf-8'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
try { $listener.Start() }
catch {
  Bad "Could not open port $port - something else is using it."
  Say 'Close whatever is on that port and run this again.'
  Read-Host '  Press Enter to close'
  exit 1
}

Write-Host ''
Good "Serving $root"
Say  "Deck: $deck"
if (-not $modelReady) { Warn 'Live chat is unavailable, but every slide still works.' }
Write-Host ''
Write-Host '  Keep this window open while you present. Closing it stops the server.' -ForegroundColor Yellow
Write-Host ''

Start-Process $deck

$rootFull = [System.IO.Path]::GetFullPath($root)

try {
  while ($listener.IsListening) {
    $context  = $listener.GetContext()
    $request  = $context.Request
    $response = $context.Response
    $path     = [System.Uri]::UnescapeDataString($request.Url.AbsolutePath)

    try {
      # ---- proxy: /ollama/* -> Ollama, same origin as the page ----
      if ($path -like '/ollama/*') {
        $target = $ollamaU + $path.Substring(7)
        $body = $null
        if ($request.HasEntityBody) {
          $reader = New-Object System.IO.StreamReader($request.InputStream, $request.ContentEncoding)
          $body = $reader.ReadToEnd(); $reader.Close()
        }
        try {
          if ($request.HttpMethod -eq 'POST') {
            $up = Invoke-WebRequest -Uri $target -Method Post -Body $body -ContentType 'application/json' `
                    -TimeoutSec 600 -UseBasicParsing
          } else {
            $up = Invoke-WebRequest -Uri $target -Method Get -TimeoutSec 60 -UseBasicParsing
          }
          $bytes = [System.Text.Encoding]::UTF8.GetBytes($up.Content)
          $response.StatusCode  = [int]$up.StatusCode
          $response.ContentType = 'application/json; charset=utf-8'
          $response.ContentLength64 = $bytes.Length
          $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } catch {
          $err = @{ error = ("Ollama did not answer: " + $_.Exception.Message) } | ConvertTo-Json
          $bytes = [System.Text.Encoding]::UTF8.GetBytes($err)
          $response.StatusCode  = 502
          $response.ContentType = 'application/json; charset=utf-8'
          $response.ContentLength64 = $bytes.Length
          $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        $response.Close()
        continue
      }

      # ---- static files ----
      $rel = $path.TrimStart('/')
      if ([string]::IsNullOrWhiteSpace($rel)) { $rel = 'slides/ai-fundamentals.html' }
      $full = [System.IO.Path]::GetFullPath((Join-Path $root ($rel -replace '/', '\')))

      if (-not $full.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        $response.StatusCode = 403
      } elseif (Test-Path -LiteralPath $full -PathType Leaf) {
        $ext  = [System.IO.Path]::GetExtension($full).ToLowerInvariant()
        $type = $mime[$ext]; if (-not $type) { $type = 'application/octet-stream' }
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
    } catch {
      try { $response.StatusCode = 500 } catch {}
    }
    try { $response.Close() } catch {}
  }
} finally {
  $listener.Stop(); $listener.Close()
}
