# Personal Life OS - Windows Setup Script
# Run: PowerShell -ExecutionPolicy Bypass -File scripts\setup.ps1

Write-Host "Personal Life OS - Setup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# 1. Copy .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example -- EDIT IT with your DB password!" -ForegroundColor Yellow
} else {
    Write-Host ".env already exists, skipping." -ForegroundColor Green
}

# 2. Backend venv
Write-Host "`nSetting up Python virtual environment..." -ForegroundColor Cyan
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Python dependencies installed." -ForegroundColor Green

# 3. Init database
Write-Host "`nInitialising database..." -ForegroundColor Cyan
python db\init_db.py
python ..\scripts\seed_activities.py
Write-Host "Database ready." -ForegroundColor Green
Set-Location ..

# 4. Frontend
Write-Host "`nInstalling frontend dependencies..." -ForegroundColor Cyan
Set-Location frontend
npm install
Set-Location ..
Write-Host "Frontend ready." -ForegroundColor Green

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Start the API:      cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8080"
Write-Host "Start the frontend: cd frontend && npm run dev"
Write-Host "API docs:           http://localhost:8080/docs"
Write-Host "Dashboard:          http://localhost:3000"
