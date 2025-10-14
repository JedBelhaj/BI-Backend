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
    st.header("📊 Budget Management")
    
    # Create tabs for different budget views
    tab1, tab2, tab3 = st.tabs(["Legacy Budgets", "Budget Data", "Budget Summary"])
    
    with tab1:
        st.subheader("Legacy Budget System")
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
        else:
            st.info("No legacy budgets found.")
    
    with tab2:
        st.subheader("Budget Data (New Schema)")
        
        # Fetch budget data
        budget_data = fetch_data("budget-data")
        
        if budget_data:
            df_budget = pd.DataFrame(budget_data)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Entries", len(df_budget))
            with col2:
                st.metric("Total Budget", f"€{df_budget['budget_amount'].sum():,.2f}")
            with col3:
                st.metric("Fiscal Years", df_budget['fiscal_year'].nunique())
            with col4:
                st.metric("Departments", df_budget['department'].nunique())
            
            # Filters
            st.subheader("Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_years = st.multiselect(
                    "Fiscal Years", 
                    options=sorted(df_budget['fiscal_year'].unique()),
                    default=sorted(df_budget['fiscal_year'].unique())
                )
            
            with col2:
                selected_categories = st.multiselect(
                    "Budget Categories", 
                    options=df_budget['budget_category'].unique(),
                    default=df_budget['budget_category'].unique()
                )
            
            with col3:
                selected_departments = st.multiselect(
                    "Departments", 
                    options=df_budget['department'].unique(),
                    default=df_budget['department'].unique()
                )
            
            # Filter data
            filtered_df = df_budget[
                (df_budget['fiscal_year'].isin(selected_years)) & 
                (df_budget['budget_category'].isin(selected_categories)) &
                (df_budget['department'].isin(selected_departments))
            ]
            
            # Display filtered metrics
            if len(filtered_df) > 0:
                st.subheader("Filtered Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filtered Entries", len(filtered_df))
                with col2:
                    st.metric("Filtered Budget", f"€{filtered_df['budget_amount'].sum():,.2f}")
                with col3:
                    avg_budget = filtered_df['budget_amount'].mean()
                    st.metric("Average Budget", f"€{avg_budget:,.2f}")
                
                # Budget breakdown chart
                if len(filtered_df) > 1:
                    st.subheader("Budget Breakdown by Category")
                    category_breakdown = filtered_df.groupby('budget_category')['budget_amount'].sum().reset_index()
                    st.bar_chart(category_breakdown.set_index('budget_category'))
                
                # Data table
                st.subheader("Budget Data Details")
                display_df = filtered_df[[
                    'fiscal_year', 'budget_category', 'budget_item', 
                    'budget_amount', 'department', 'account_code', 
                    'sheet_source', 'processed_date'
                ]].copy()
                
                st.dataframe(
                    display_df,
                    column_config={
                        "fiscal_year": "Year",
                        "budget_category": "Category",
                        "budget_item": "Item",
                        "budget_amount": st.column_config.NumberColumn("Amount (€)", format="€%.2f"),
                        "department": "Department",
                        "account_code": "Account Code",
                        "sheet_source": "Source Sheet",
                        "processed_date": "Processed Date"
                    },
                    use_container_width=True
                )
            else:
                st.warning("No data matches the selected filters.")
        else:
            st.info("No budget data found.")
            
            # Add form to create budget data
            with st.expander("➕ Add Budget Data Entry"):
                with st.form("budget_data_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sheet_source = st.text_input("Sheet Source", "FY2025_Budget_Q1.xlsx")
                        fiscal_year = st.number_input("Fiscal Year", min_value=2020, max_value=2030, value=2025)
                        processed_date = st.date_input("Processed Date", pd.Timestamp.now().date())
                        budget_category = st.text_input("Budget Category", "Operations")
                    
                    with col2:
                        budget_item = st.text_input("Budget Item", "Office Supplies")
                        budget_amount = st.number_input("Budget Amount", min_value=0.0, value=1000.0, step=100.0)
                        department = st.text_input("Department", "Administration")
                        account_code = st.text_input("Account Code", "OP-001")
                    
                    budget_description = st.text_area("Description", "Budget item description")
                    
                    if st.form_submit_button("Add Budget Data"):
                        new_entry = {
                            "sheet_source": sheet_source,
                            "fiscal_year": fiscal_year,
                            "processed_date": processed_date.strftime("%Y-%m-%d"),
                            "budget_category": budget_category,
                            "budget_item": budget_item,
                            "budget_amount": budget_amount,
                            "budget_description": budget_description,
                            "department": department,
                            "account_code": account_code
                        }
                        
                        if post_data("budget-data", new_entry):
                            st.success("Budget data entry created successfully!")
                            st.rerun()
    
    with tab3:
        st.subheader("Budget Summary (New Schema)")
        
        # Fetch budget summary
        budget_summary = fetch_data("budget-summary")
        
        if budget_summary:
            df_summary = pd.DataFrame(budget_summary)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Summary Entries", len(df_summary))
            with col2:
                st.metric("Total Budget Amount", f"€{df_summary['total_budget_amount'].sum():,.2f}")
            with col3:
                st.metric("Total Records", df_summary['total_records'].sum())
            
            # Data table
            st.subheader("Summary Details")
            display_summary = df_summary[[
                'sheet_name', 'fiscal_year', 'total_records', 
                'total_budget_amount', 'max_budget_item', 
                'min_budget_item', 'average_budget_item', 'processing_date'
            ]].copy()
            
            st.dataframe(
                display_summary,
                column_config={
                    "sheet_name": "Sheet Name",
                    "fiscal_year": "Fiscal Year", 
                    "total_records": "Records",
                    "total_budget_amount": st.column_config.NumberColumn("Total (€)", format="€%.2f"),
                    "max_budget_item": st.column_config.NumberColumn("Max Item (€)", format="€%.2f"),
                    "min_budget_item": st.column_config.NumberColumn("Min Item (€)", format="€%.2f"),
                    "average_budget_item": st.column_config.NumberColumn("Avg Item (€)", format="€%.2f"),
                    "processing_date": "Processing Date"
                },
                use_container_width=True
            )
            
            # Summary chart
            if len(df_summary) > 1:
                st.subheader("Budget Summary by Fiscal Year")
                yearly_summary = df_summary.groupby('fiscal_year')['total_budget_amount'].sum().reset_index()
                st.bar_chart(yearly_summary.set_index('fiscal_year'))
        else:
            st.info("No budget summary found.")

# Footer
st.sidebar.divider()
st.sidebar.info("Connect to Django backend at http://localhost:8000")
