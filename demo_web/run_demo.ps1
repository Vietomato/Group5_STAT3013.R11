param([int]$Port = 8501)
$ErrorActionPreference = 'Stop'
$demoRoot = Split-Path -Parent $PSScriptRoot
$demoPython = Join-Path $demoRoot '.venv-boosting/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $demoPython)) {
    $demoPython = Join-Path $demoRoot '.venv/Scripts/python.exe'
}
if (-not (Test-Path -LiteralPath $demoPython)) {
    $demoPython = 'python'
}
Write-Host "Open http://127.0.0.1:$Port when the model is ready. Stop with Ctrl+C."
& $demoPython (Join-Path $PSScriptRoot 'server.py') --port $Port
exit $LASTEXITCODE
