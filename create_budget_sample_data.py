#!/usr/bin/env python3
"""
Create sample budget data for the new schema
"""
import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_backend.settings')
django.setup()

from finance.models import BudgetData, BudgetSummary

def create_sample_budget_data():
    """Create sample budget data entries"""
    
    print("Creating sample budget data...")
    
    # Sample budget data entries
    budget_entries = [
        {
            'sheet_source': 'FY2024_Budget_Q1.xlsx',
            'fiscal_year': 2024,
            'processed_date': date(2024, 1, 15),
            'budget_category': 'Operations',
            'budget_item': 'Office Supplies',
            'budget_amount': Decimal('12000.00'),
            'budget_description': 'Paper, pens, printer supplies, and other office necessities',
            'department': 'Administration',
            'account_code': 'OP-001',
        },
        {
            'sheet_source': 'FY2024_Budget_Q1.xlsx',
            'fiscal_year': 2024,
            'processed_date': date(2024, 1, 15),
            'budget_category': 'Operations',
            'budget_item': 'Travel & Expenses',
            'budget_amount': Decimal('25000.00'),
            'budget_description': 'Business travel, accommodation, and meal expenses',
            'department': 'Sales',
            'account_code': 'OP-002',
        },
        {
            'sheet_source': 'FY2024_Budget_Q1.xlsx',
            'fiscal_year': 2024,
            'processed_date': date(2024, 1, 15),
            'budget_category': 'Technology',
            'budget_item': 'Software Licenses',
            'budget_amount': Decimal('18000.00'),
            'budget_description': 'Annual software licenses and subscriptions',
            'department': 'IT',
            'account_code': 'IT-001',
        },
        {
            'sheet_source': 'FY2024_Budget_Q2.xlsx',
            'fiscal_year': 2024,
            'processed_date': date(2024, 4, 10),
            'budget_category': 'Marketing',
            'budget_item': 'Digital Advertising',
            'budget_amount': Decimal('35000.00'),
            'budget_description': 'Online advertising campaigns and social media marketing',
            'department': 'Marketing',
            'account_code': 'MK-001',
        },
        {
            'sheet_source': 'FY2024_Budget_Q2.xlsx',
            'fiscal_year': 2024,
            'processed_date': date(2024, 4, 10),
            'budget_category': 'Human Resources',
            'budget_item': 'Training & Development',
            'budget_amount': Decimal('15000.00'),
            'budget_description': 'Employee training programs and professional development',
            'department': 'HR',
            'account_code': 'HR-001',
        },
        {
            'sheet_source': 'FY2025_Budget_Q1.xlsx',
            'fiscal_year': 2025,
            'processed_date': date(2025, 1, 20),
            'budget_category': 'Operations',
            'budget_item': 'Facility Maintenance',
            'budget_amount': Decimal('22000.00'),
            'budget_description': 'Building maintenance, utilities, and cleaning services',
            'department': 'Facilities',
            'account_code': 'OP-003',
        },
    ]
    
    created_count = 0
    for entry in budget_entries:
        budget_data, created = BudgetData.objects.get_or_create(
            sheet_source=entry['sheet_source'],
            fiscal_year=entry['fiscal_year'],
            budget_category=entry['budget_category'],
            budget_item=entry['budget_item'],
            defaults=entry
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {budget_data}")
        else:
            print(f"⚠️  Already exists: {budget_data}")
    
    print(f"\nCreated {created_count} new budget data entries.")
    return created_count

def create_sample_budget_summary():
    """Create sample budget summary entries"""
    
    print("\nCreating sample budget summary...")
    
    # Calculate summaries from the budget data
    summary_entries = [
        {
            'sheet_name': 'FY2024_Budget_Q1.xlsx',
            'fiscal_year': 2024,
            'total_records': 3,
            'total_budget_amount': Decimal('55000.00'),
            'max_budget_item': Decimal('25000.00'),
            'min_budget_item': Decimal('12000.00'),
            'average_budget_item': Decimal('18333.33'),
            'processing_date': datetime(2024, 1, 15, 10, 30, 0),
        },
        {
            'sheet_name': 'FY2024_Budget_Q2.xlsx',
            'fiscal_year': 2024,
            'total_records': 2,
            'total_budget_amount': Decimal('50000.00'),
            'max_budget_item': Decimal('35000.00'),
            'min_budget_item': Decimal('15000.00'),
            'average_budget_item': Decimal('25000.00'),
            'processing_date': datetime(2024, 4, 10, 14, 15, 0),
        },
        {
            'sheet_name': 'FY2025_Budget_Q1.xlsx',
            'fiscal_year': 2025,
            'total_records': 1,
            'total_budget_amount': Decimal('22000.00'),
            'max_budget_item': Decimal('22000.00'),
            'min_budget_item': Decimal('22000.00'),
            'average_budget_item': Decimal('22000.00'),
            'processing_date': datetime(2025, 1, 20, 9, 45, 0),
        },
    ]
    
    created_count = 0
    for entry in summary_entries:
        summary, created = BudgetSummary.objects.get_or_create(
            sheet_name=entry['sheet_name'],
            fiscal_year=entry['fiscal_year'],
            defaults=entry
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {summary}")
        else:
            print(f"⚠️  Already exists: {summary}")
    
    print(f"\nCreated {created_count} new budget summary entries.")
    return created_count

def main():
    """Main function"""
    print("🚀 Creating Sample Budget Data")
    print("=" * 50)
    
    # Create budget data
    budget_count = create_sample_budget_data()
    
    # Create budget summaries
    summary_count = create_sample_budget_summary()
    
    # Show totals
    total_budget_data = BudgetData.objects.count()
    total_budget_summary = BudgetSummary.objects.count()
    
    print("\n📊 Database Summary:")
    print(f"   Total Budget Data entries: {total_budget_data}")
    print(f"   Total Budget Summary entries: {total_budget_summary}")
    
    print("\n✅ Sample data creation complete!")

if __name__ == "__main__":
    main()