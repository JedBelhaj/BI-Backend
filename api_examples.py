"""
API Usage Examples for Django Financial Backend

This file demonstrates how to interact with the Django backend API
from Python using the requests library.
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
BASE_URL = "http://localhost:8000/api"
headers = {"Content-Type": "application/json"}


def print_response(response, title="Response"):
    """Helper function to print API responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code < 300:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")


# ============================================================================
# ACCOUNTS
# ============================================================================

def create_account():
    """Create a new account"""
    url = f"{BASE_URL}/accounts/"
    data = {
        "name": "My Checking Account",
        "account_type": "CHECKING",
        "currency": "USD",
        "description": "Primary checking account",
        "is_active": True
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "Create Account")
    return response.json() if response.status_code == 201 else None


def get_accounts():
    """Get all accounts"""
    url = f"{BASE_URL}/accounts/"
    response = requests.get(url)
    print_response(response, "Get All Accounts")
    return response.json()


def get_account_summary():
    """Get account summary"""
    url = f"{BASE_URL}/accounts/summary/"
    response = requests.get(url)
    print_response(response, "Account Summary")
    return response.json()


def update_account(account_id, data):
    """Update an account"""
    url = f"{BASE_URL}/accounts/{account_id}/"
    response = requests.patch(url, json=data, headers=headers)
    print_response(response, "Update Account")
    return response.json()


# ============================================================================
# CATEGORIES
# ============================================================================

def create_category():
    """Create a new category"""
    url = f"{BASE_URL}/categories/"
    data = {
        "name": "Restaurant",
        "category_type": "EXPENSE",
        "description": "Dining out and restaurants",
        "color": "#ff6b6b",
        "is_active": True
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "Create Category")
    return response.json() if response.status_code == 201 else None


def get_categories(category_type=None):
    """Get all categories, optionally filtered by type"""
    url = f"{BASE_URL}/categories/"
    params = {}
    if category_type:
        params['category_type'] = category_type
    
    response = requests.get(url, params=params)
    print_response(response, f"Get Categories (type={category_type})")
    return response.json()


# ============================================================================
# TRANSACTIONS
# ============================================================================

def create_transaction(account_id, category_id):
    """Create a new transaction"""
    url = f"{BASE_URL}/transactions/"
    data = {
        "account": account_id,
        "category": category_id,
        "transaction_type": "EXPENSE",
        "amount": "75.50",
        "date": datetime.now().date().isoformat(),
        "description": "Grocery shopping at Whole Foods",
        "is_recurring": False
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "Create Transaction")
    return response.json() if response.status_code == 201 else None


def get_transactions(start_date=None, end_date=None, transaction_type=None):
    """Get transactions with optional filters"""
    url = f"{BASE_URL}/transactions/"
    params = {}
    
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    if transaction_type:
        params['transaction_type'] = transaction_type
    
    response = requests.get(url, params=params)
    print_response(response, "Get Transactions")
    return response.json()


def get_transaction_summary():
    """Get transaction summary"""
    url = f"{BASE_URL}/transactions/summary/"
    response = requests.get(url)
    print_response(response, "Transaction Summary")
    return response.json()


def get_transactions_by_category():
    """Get transactions grouped by category"""
    url = f"{BASE_URL}/transactions/by_category/"
    response = requests.get(url)
    print_response(response, "Transactions by Category")
    return response.json()


def get_monthly_summary():
    """Get monthly transaction summary"""
    url = f"{BASE_URL}/transactions/monthly_summary/"
    response = requests.get(url)
    print_response(response, "Monthly Summary")
    return response.json()


# ============================================================================
# BUDGETS
# ============================================================================

def create_budget(category_id):
    """Create a new budget"""
    url = f"{BASE_URL}/budgets/"
    today = datetime.now().date()
    next_month = today + timedelta(days=30)
    
    data = {
        "category": category_id,
        "amount": "500.00",
        "start_date": today.isoformat(),
        "end_date": next_month.isoformat(),
        "notes": "Monthly food budget",
        "is_active": True
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response, "Create Budget")
    return response.json() if response.status_code == 201 else None


def get_budgets():
    """Get all budgets"""
    url = f"{BASE_URL}/budgets/"
    response = requests.get(url)
    print_response(response, "Get All Budgets")
    return response.json()


def get_current_budgets():
    """Get currently active budgets"""
    url = f"{BASE_URL}/budgets/current/"
    response = requests.get(url)
    print_response(response, "Current Active Budgets")
    return response.json()


# ============================================================================
# EXAMPLE WORKFLOW
# ============================================================================

def demo_workflow():
    """Demonstrate a complete workflow"""
    print("\n" + "="*60)
    print("DEMO WORKFLOW: Complete Financial Data Entry")
    print("="*60)
    
    # 1. Create an account
    print("\n1. Creating a new account...")
    account = create_account()
    if not account:
        print("Failed to create account")
        return
    account_id = account['id']
    
    # 2. Create a category
    print("\n2. Creating a new category...")
    category = create_category()
    if not category:
        print("Failed to create category")
        return
    category_id = category['id']
    
    # 3. Create a transaction
    print("\n3. Creating a new transaction...")
    transaction = create_transaction(account_id, category_id)
    if not transaction:
        print("Failed to create transaction")
        return
    
    # 4. Create a budget
    print("\n4. Creating a new budget...")
    budget = create_budget(category_id)
    
    # 5. Get summaries
    print("\n5. Getting account summary...")
    get_account_summary()
    
    print("\n6. Getting transaction summary...")
    get_transaction_summary()
    
    print("\n7. Getting current budgets...")
    get_current_budgets()
    
    print("\n" + "="*60)
    print("DEMO WORKFLOW COMPLETED")
    print("="*60)


def demo_queries():
    """Demonstrate various query options"""
    print("\n" + "="*60)
    print("DEMO QUERIES: Filtering and Analysis")
    print("="*60)
    
    # Get all accounts
    print("\n1. All Accounts:")
    get_accounts()
    
    # Get income categories only
    print("\n2. Income Categories:")
    get_categories(category_type="INCOME")
    
    # Get expense categories only
    print("\n3. Expense Categories:")
    get_categories(category_type="EXPENSE")
    
    # Get transactions from last 30 days
    print("\n4. Transactions (Last 30 Days):")
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    get_transactions(start_date=start_date.isoformat(), end_date=end_date.isoformat())
    
    # Get only expense transactions
    print("\n5. Expense Transactions Only:")
    get_transactions(transaction_type="EXPENSE")
    
    # Get transactions grouped by category
    print("\n6. Transactions by Category:")
    get_transactions_by_category()
    
    # Get monthly summary
    print("\n7. Monthly Summary:")
    get_monthly_summary()
    
    # Get all budgets
    print("\n8. All Budgets:")
    get_budgets()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║   Django Financial Backend - API Usage Examples           ║
║                                                            ║
║   Make sure the Django server is running:                 ║
║   python manage.py runserver                              ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n" + "="*60)
        print("Select an option:")
        print("="*60)
        print("1. Demo Workflow (Create account, category, transaction, budget)")
        print("2. Demo Queries (Various filtering and analysis examples)")
        print("3. Create Account")
        print("4. Get All Accounts")
        print("5. Get Account Summary")
        print("6. Create Category")
        print("7. Get All Categories")
        print("8. Get Transaction Summary")
        print("9. Get Transactions by Category")
        print("10. Get Monthly Summary")
        print("11. Get Current Budgets")
        print("0. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("\nGoodbye!")
            break
        elif choice == "1":
            demo_workflow()
        elif choice == "2":
            demo_queries()
        elif choice == "3":
            create_account()
        elif choice == "4":
            get_accounts()
        elif choice == "5":
            get_account_summary()
        elif choice == "6":
            create_category()
        elif choice == "7":
            get_categories()
        elif choice == "8":
            get_transaction_summary()
        elif choice == "9":
            get_transactions_by_category()
        elif choice == "10":
            get_monthly_summary()
        elif choice == "11":
            get_current_budgets()
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
