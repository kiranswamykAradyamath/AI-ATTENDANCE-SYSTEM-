$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot ".pip-cache"
$env:TEMP = Join-Path $ProjectRoot ".tmp"
$env:TMP = Join-Path $ProjectRoot ".tmp"

New-Item -ItemType Directory -Force -Path $env:PIP_CACHE_DIR, $env:TEMP | Out-Null

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$TempRequirements = Join-Path $env:TEMP "requirements-without-resemblyzer.txt"

Get-Content $Requirements |
    Where-Object { $_.Trim() -ne "resemblyzer" } |
    Set-Content $TempRequirements

& $Python -m pip install -r $TempRequirements
& $Python -m pip install --no-deps resemblyzer
