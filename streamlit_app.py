"""
Sample Streamlit app to connect to the Django backend
Install streamlit: pip install streamlit requests pandas
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(page_title="Financial Dashboard", page_icon="💰", layout="wide")

# Helper functions
def fetch_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

def post_data(endpoint, data):
    """Post data to API endpoint"""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error posting data: {e}")
        return None

# Main app
st.title("💰 Financial Management Dashboard")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Accounts", "Transactions", "Categories", "Budgets"]
)

if page == "Dashboard":
    st.header("Overview")
    
    col1, col2, col3 = st.columns(3)
    
    # Fetch account summary
    accounts_data = fetch_data("accounts")
    if accounts_data:
        results = accounts_data.get('results', accounts_data)
        if isinstance(results, list):
            total_balance = sum(float(acc.get('balance', 0)) for acc in results)
            active_accounts = len([acc for acc in results if acc.get('is_active', False)])
            
            with col1:
                st.metric("Total Balance", f"${total_balance:,.2f}")
            with col2:
                st.metric("Active Accounts", active_accounts)
    
    # Fetch transaction summary
    transactions_summary = fetch_data("transactions/summary")
    if transactions_summary:
        with col3:
            net_balance = float(transactions_summary.get('net_balance', 0))
            st.metric("Net Balance", f"${net_balance:,.2f}")
        
        col4, col5 = st.columns(2)
        with col4:
            income = float(transactions_summary.get('total_income', 0))
            st.metric("Total Income", f"${income:,.2f}", delta="Income")
        with col5:
            expenses = float(transactions_summary.get('total_expenses', 0))
            st.metric("Total Expenses", f"${expenses:,.2f}", delta="Expenses", delta_color="inverse")
    
    st.divider()
    
    # Recent transactions
    st.subheader("Recent Transactions")
    transactions_data = fetch_data("transactions")
    if transactions_data:
        results = transactions_data.get('results', transactions_data)
        if isinstance(results, list) and results:
            df = pd.DataFrame(results[:10])  # Show last 10 transactions
            df = df[['date', 'account_name', 'category_name', 'transaction_type', 'amount', 'description']]
            st.dataframe(df, use_container_width=True)

elif page == "Accounts":
    st.header("Accounts")
    
    # Display accounts
    accounts_data = fetch_data("accounts")
    if accounts_data:
        results = accounts_data.get('results', accounts_data)
        if isinstance(results, list):
            df = pd.DataFrame(results)
            if not df.empty:
                df = df[['name', 'account_type', 'balance', 'currency', 'is_active']]
                st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Add new account
    st.subheader("Add New Account")
    with st.form("new_account"):
        name = st.text_input("Account Name")
        account_type = st.selectbox("Account Type", 
            ['CHECKING', 'SAVINGS', 'CREDIT', 'CASH', 'INVESTMENT', 'OTHER'])
        currency = st.text_input("Currency", value="USD")
        description = st.text_area("Description")
        
        if st.form_submit_button("Create Account"):
            data = {
                "name": name,
                "account_type": account_type,
                "currency": currency,
                "description": description,
                "is_active": True
            }
            result = post_data("accounts", data)
            if result:
                st.success(f"Account '{name}' created successfully!")
                st.rerun()

elif page == "Transactions":
    st.header("Transactions")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        transaction_type = st.selectbox("Type", ["All", "INCOME", "EXPENSE", "TRANSFER"])
    with col2:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col3:
        end_date = st.date_input("End Date", datetime.now())
    
    # Fetch transactions
    params = f"?start_date={start_date}&end_date={end_date}"
    if transaction_type != "All":
        params += f"&transaction_type={transaction_type}"
    
    transactions_data = fetch_data(f"transactions{params}")
    if transactions_data:
        results = transactions_data.get('results', transactions_data)
        if isinstance(results, list):
            df = pd.DataFrame(results)
            if not df.empty:
                df = df[['date', 'account_name', 'category_name', 'transaction_type', 
                        'amount', 'description', 'created_at']]
                st.dataframe(df, use_container_width=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"transactions_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
    
    st.divider()
    
    # Add new transaction
    st.subheader("Add New Transaction")
    
    # Fetch accounts and categories
    accounts = fetch_data("accounts")
    categories = fetch_data("categories")
    
    if accounts and categories:
        accounts_list = accounts.get('results', accounts)
        categories_list = categories.get('results', categories)
        
        with st.form("new_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                account_options = {acc['name']: acc['id'] for acc in accounts_list if isinstance(accounts_list, list)}
                selected_account = st.selectbox("Account", list(account_options.keys()))
                
                trans_type = st.selectbox("Type", ['INCOME', 'EXPENSE', 'TRANSFER'])
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
            
            with col2:
                category_options = {cat['name']: cat['id'] for cat in categories_list if isinstance(categories_list, list)}
                selected_category = st.selectbox("Category", list(category_options.keys()))
                
                date = st.date_input("Date", datetime.now())
            
            description = st.text_area("Description")
            
            if st.form_submit_button("Add Transaction"):
                data = {
                    "account": account_options[selected_account],
                    "category": category_options[selected_category],
                    "transaction_type": trans_type,
                    "amount": str(amount),
                    "date": str(date),
                    "description": description
                }
                result = post_data("transactions", data)
                if result:
                    st.success("Transaction added successfully!")
                    st.rerun()

elif page == "Categories":
    st.header("Categories")
    
    # Display categories
    categories_data = fetch_data("categories")
    if categories_data:
        results = categories_data.get('results', categories_data)
        if isinstance(results, list):
            df = pd.DataFrame(results)
            if not df.empty:
                df = df[['name', 'category_type', 'color', 'is_active', 'transaction_count']]
                st.dataframe(df, use_container_width=True)

elif page == "Budgets":
    st.header("Budgets")
    
    # Display current budgets
    budgets_data = fetch_data("budgets/current")
    if budgets_data:
        if isinstance(budgets_data, list):
            for budget in budgets_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Category", budget['category_name'])
                with col2:
                    st.metric("Budget", f"${float(budget['amount']):,.2f}")
                with col3:
                    spent = float(budget['spent_amount'])
                    remaining = float(budget['remaining_amount'])
                    st.metric("Spent", f"${spent:,.2f}")
                
                # Progress bar
                progress = budget['progress_percentage']
                st.progress(min(progress / 100, 1.0))
                st.text(f"{progress:.1f}% used | ${remaining:,.2f} remaining")
                st.divider()

# Footer
st.sidebar.divider()
st.sidebar.info("Connect to Django backend at http://localhost:8000")
