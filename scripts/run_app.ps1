$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot ".pip-cache"
$env:TEMP = Join-Path $ProjectRoot ".tmp"
$env:TMP = Join-Path $ProjectRoot ".tmp"
$env:DEEPFACE_HOME = $ProjectRoot
# Fix Windows UnicodeEncodeError from DeepFace emoji log messages
$env:PYTHONIOENCODING = "utf-8"

Set-Location $ProjectRoot
& (Join-Path $ProjectRoot "venv\Scripts\streamlit.exe") run app.py
