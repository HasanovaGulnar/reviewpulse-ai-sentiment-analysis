$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Virtual environment is missing. Follow README.md setup first."
}

& .\.venv\Scripts\python.exe -m streamlit run app.py
