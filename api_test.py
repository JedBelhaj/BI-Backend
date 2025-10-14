#!/usr/bin/env python3
"""
Comprehensive API test for the Django backend
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test API endpoint"""
    url = f"{API_BASE}/{endpoint}/"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200 and method == "GET":
            data = response.json()
            if isinstance(data, list):
                print(f"   📊 Returned {len(data)} items")
            else:
                print(f"   📊 Returned data")
        elif response.status_code == 201 and method == "POST":
            print(f"   ✨ Created successfully")
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint}: {e}")
        return None

def main():
    print("🚀 Comprehensive Django API Test")
    print("=" * 50)
    
    # Test all endpoints
    endpoints = [
        "accounts", 
        "categories", 
        "transactions", 
        "budgets",
        "budget-data",
        "budget-summary"
    ]
    
    print("\n📋 Testing GET endpoints:")
    for endpoint in endpoints:
        test_endpoint(endpoint)
    
    print(f"\n✨ All tests completed!")
    print(f"\n🌐 Django Server: http://localhost:8000/")
    print(f"🌐 Streamlit App: http://localhost:8501/")
    print(f"🔧 Django Admin: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()