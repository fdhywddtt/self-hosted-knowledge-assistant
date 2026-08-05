$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -e "backend[dev]"
Push-Location backend
& ..\.venv\Scripts\alembic.exe upgrade head
Pop-Location

Write-Host "后端启动: http://localhost:8000/docs"
& .\.venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --port 8000
