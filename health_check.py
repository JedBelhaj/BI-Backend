"""
Quick Health Check Script for Django Financial Backend
Run this script to verify that your Django backend is working correctly.

Usage: python health_check.py
"""

import requests
import sys
import json
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, success=True):
    """Print status message with color"""
    color = Colors.GREEN if success else Colors.RED
    symbol = "✅" if success else "❌"
    print(f"{color}{symbol} {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_header(message):
    """Print section header"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"🧪 {message}")
    print(f"{'='*60}{Colors.END}")

def test_server_connection():
    """Test if Django server is running"""
    print_header("Testing Server Connection")
    
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK, means server is running
            print_status("Django server is running")
            return True
        else:
            print_status(f"Server returned status code: {response.status_code}", False)
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to Django server", False)
        print_info("Make sure the server is running: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print_status("Server connection timed out", False)
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("Testing API Endpoints")
    
    base_url = 'http://localhost:8000/api'
    endpoints = {
        'API Root': '',
        'Accounts': '/accounts/',
        'Categories': '/categories/', 
        'Transactions': '/transactions/',
        'Budgets': '/budgets/'
    }
    
    all_passed = True
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if endpoint:  # Not root endpoint
                    count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                    print_status(f"{name} endpoint working ({count} records)")
                else:
                    print_status(f"{name} accessible")
            else:
                print_status(f"{name} endpoint failed (status: {response.status_code})", False)
                all_passed = False
        except Exception as e:
            print_status(f"{name} endpoint error: {str(e)}", False)
            all_passed = False
    
    return all_passed

def test_api_features():
    """Test specific API features"""
    print_header("Testing API Features")
    
    base_url = 'http://localhost:8000/api'
    features = {
        'Transaction Summary': '/transactions/summary/',
        'Transactions by Category': '/transactions/by_category/',
        'Monthly Summary': '/transactions/monthly_summary/',
        'Account Summary': '/accounts/summary/',
        'Current Budgets': '/budgets/current/'
    }
    
    all_passed = True
    
    for name, endpoint in features.items():
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_status(f"{name} working")
                
                # Show some sample data
                if name == 'Transaction Summary' and isinstance(data, dict):
                    income = data.get('total_income', 0)
                    expenses = data.get('total_expenses', 0)
                    net = data.get('net_balance', 0)
                    print_info(f"  Income: ${income}, Expenses: ${expenses}, Net: ${net}")
                    
            else:
                print_status(f"{name} failed (status: {response.status_code})", False)
                all_passed = False
        except Exception as e:
            print_status(f"{name} error: {str(e)}", False)
            all_passed = False
    
    return all_passed

def test_data_creation():
    """Test creating data through API"""
    print_header("Testing Data Creation")
    
    # Test creating an account
    try:
        account_data = {
            "name": f"Test Account {datetime.now().strftime('%H%M%S')}",
            "account_type": "CHECKING",
            "currency": "USD",
            "description": "Health check test account",
            "is_active": True
        }
        
        response = requests.post('http://localhost:8000/api/accounts/', 
                               json=account_data, timeout=5)
        
        if response.status_code == 201:
            print_status("Account creation working")
            account_id = response.json()['id']
            
            # Clean up - delete the test account
            requests.delete(f'http://localhost:8000/api/accounts/{account_id}/')
            print_info("Test account cleaned up")
            
        else:
            print_status(f"Account creation failed (status: {response.status_code})", False)
            return False
            
    except Exception as e:
        print_status(f"Account creation error: {str(e)}", False)
        return False
    
    return True

def test_filtering():
    """Test API filtering capabilities"""
    print_header("Testing API Filtering")
    
    try:
        # Test date filtering
        response = requests.get('http://localhost:8000/api/transactions/?start_date=2024-01-01', timeout=5)
        if response.status_code == 200:
            print_status("Date filtering working")
        else:
            print_status("Date filtering failed", False)
            return False
            
        # Test type filtering
        response = requests.get('http://localhost:8000/api/transactions/?transaction_type=EXPENSE', timeout=5)
        if response.status_code == 200:
            print_status("Type filtering working")
        else:
            print_status("Type filtering failed", False)
            return False
            
    except Exception as e:
        print_status(f"Filtering error: {str(e)}", False)
        return False
    
    return True

def test_admin_access():
    """Test admin panel accessibility"""
    print_header("Testing Admin Panel")
    
    try:
        response = requests.get('http://localhost:8000/admin/', timeout=5)
        if response.status_code == 200:
            print_status("Admin panel accessible")
            return True
        else:
            print_status(f"Admin panel failed (status: {response.status_code})", False)
            return False
    except Exception as e:
        print_status(f"Admin panel error: {str(e)}", False)
        return False

def run_comprehensive_test():
    """Run all tests"""
    print(f"{Colors.BOLD}🧪 Django Financial Backend - Health Check{Colors.END}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Server Connection", test_server_connection),
        ("API Endpoints", test_api_endpoints),
        ("API Features", test_api_features),
        ("Data Creation", test_data_creation),
        ("API Filtering", test_filtering),
        ("Admin Access", test_admin_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print_warning("Test interrupted by user")
            break
        except Exception as e:
            print_status(f"{test_name} test crashed: {str(e)}", False)
            results.append((test_name, False))
    
    # Final report
    print_header("Test Results Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_status(f"{test_name}: {'PASSED' if result else 'FAILED'}", result)
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("🎉 ALL TESTS PASSED!")
        print("Your Django Financial Backend is working correctly!")
        print("You can now:")
        print("  • Use the admin panel: http://localhost:8000/admin/")
        print("  • Test the API: http://localhost:8000/api/")
        print("  • Run Streamlit: streamlit run streamlit_app.py")
        print(f"{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}")
        print("❌ Some tests failed!")
        print("Check the error messages above for troubleshooting.")
        print("Refer to TESTING_GUIDE.md for detailed solutions.")
        print(f"{Colors.END}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick test - just check if server is running and API works
        if test_server_connection() and test_api_endpoints():
            print_status("Quick health check passed!")
        else:
            print_status("Quick health check failed!", False)
    else:
        # Full comprehensive test
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()