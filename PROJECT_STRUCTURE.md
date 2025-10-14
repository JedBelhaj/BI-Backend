# Django Financial Backend - Clean Project Structure

## 🗂️ Core Application Files

### Main Django Files

- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `db.sqlite3` - SQLite database (contains your data)
- `.env` - Environment variables (keep this secure!)
- `.env.example` - Example environment file template
- `.gitignore` - Git ignore patterns

### Django Backend

- `financial_backend/` - Main Django project directory
  - `settings.py` - Django configuration
  - `urls.py` - URL routing
  - `wsgi.py` - WSGI configuration

### Finance App

- `finance/` - Django app for financial management
  - `models.py` - Database models (Account, Transaction, Category, BudgetData, BudgetSummary)
  - `views.py` - API views and endpoints
  - `serializers.py` - Data serialization
  - `admin.py` - Django admin configuration
  - `urls.py` - API URL routing
  - `migrations/` - Database migrations

### Frontend & Testing

- `streamlit_app.py` - Streamlit dashboard application
- `health_check.py` - System health check script
- `api_test.py` - API testing script
- `create_budget_sample_data.py` - Sample data generator

### Setup & Utilities

- `setup.ps1` - PowerShell setup script
- `README.md` - Project documentation
- `venv/` - Python virtual environment

## 🧹 Cleaned Up Files

The following unnecessary files have been removed:

- ❌ `api_examples.py` - Old API examples (no longer needed)
- ❌ `run_etl_direct.py` - ETL pipeline (abandoned feature)
- ❌ `data_recettes-annee-2024.csv` - Sample CSV data (replaced with generated data)
- ❌ `__pycache__/` directories - Python bytecode cache files
- ❌ `*.pyc` files - Compiled Python files

## 🚀 Current Running Services

- **Django Backend**: http://localhost:8000/
  - API: http://localhost:8000/api/
  - Admin: http://localhost:8000/admin/
- **Streamlit Frontend**: http://localhost:8501/

## 📋 To Do (Optional Cleanup)

You might also consider:

1. Remove `create_budget_sample_data.py` if you don't need to generate more sample data
2. Remove `api_test.py` if you don't need to run API tests regularly
3. Keep `health_check.py` - it's useful for verifying the system is working

The project is now clean and contains only the essential files needed for your Django financial backend with Streamlit frontend.
