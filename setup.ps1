# Setup script for Windows PowerShell
# Run this script to set up the Django backend

Write-Host "Setting up Django Financial Backend..." -ForegroundColor Green

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "`nCreating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please update .env file with your settings" -ForegroundColor Cyan
}

# Run migrations
Write-Host "`nRunning migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

# Create superuser
Write-Host "`nCreate a superuser for admin access:" -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Run the server: python manage.py runserver"
Write-Host "2. Access admin panel: http://localhost:8000/admin/"
Write-Host "3. API endpoints: http://localhost:8000/api/"
Write-Host "4. Run Streamlit app: streamlit run streamlit_app.py"
