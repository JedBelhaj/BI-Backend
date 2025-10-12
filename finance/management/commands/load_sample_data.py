from django.core.management.base import BaseCommand
from finance.models import Account, Category, Transaction
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Load sample financial data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')
        
        # Create sample accounts
        self.stdout.write('Creating accounts...')
        accounts = [
            Account.objects.get_or_create(
                name='Main Checking',
                defaults={
                    'account_type': 'CHECKING',
                    'balance': Decimal('5000.00'),
                    'currency': 'USD',
                    'description': 'Primary checking account'
                }
            )[0],
            Account.objects.get_or_create(
                name='Savings',
                defaults={
                    'account_type': 'SAVINGS',
                    'balance': Decimal('10000.00'),
                    'currency': 'USD',
                    'description': 'Emergency savings'
                }
            )[0],
            Account.objects.get_or_create(
                name='Credit Card',
                defaults={
                    'account_type': 'CREDIT',
                    'balance': Decimal('-1500.00'),
                    'currency': 'USD',
                    'description': 'Rewards credit card'
                }
            )[0],
        ]
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(accounts)} accounts'))
        
        # Load categories from fixture or create basic ones
        self.stdout.write('Loading categories...')
        try:
            from django.core.management import call_command
            call_command('loaddata', 'initial_categories')
            self.stdout.write(self.style.SUCCESS('Loaded categories from fixture'))
        except:
            # Create basic categories if fixture fails
            categories = [
                Category.objects.get_or_create(
                    name='Salary',
                    defaults={'category_type': 'INCOME', 'color': '#28a745'}
                )[0],
                Category.objects.get_or_create(
                    name='Groceries',
                    defaults={'category_type': 'EXPENSE', 'color': '#ffc107'}
                )[0],
                Category.objects.get_or_create(
                    name='Utilities',
                    defaults={'category_type': 'EXPENSE', 'color': '#dc3545'}
                )[0],
            ]
            self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} basic categories'))
        
        # Create sample transactions
        self.stdout.write('Creating transactions...')
        
        income_categories = Category.objects.filter(category_type='INCOME')
        expense_categories = Category.objects.filter(category_type='EXPENSE')
        
        if not income_categories.exists() or not expense_categories.exists():
            self.stdout.write(self.style.WARNING('No categories found, skipping transactions'))
            return
        
        transaction_count = 0
        today = datetime.now().date()
        
        # Create transactions for the last 90 days
        for days_ago in range(90):
            trans_date = today - timedelta(days=days_ago)
            
            # Random income transactions (less frequent)
            if days_ago % 30 == 0:  # Monthly salary
                Transaction.objects.create(
                    account=accounts[0],
                    category=random.choice(income_categories),
                    transaction_type='INCOME',
                    amount=Decimal(str(random.uniform(3000, 5000))),
                    date=trans_date,
                    description='Monthly salary payment'
                )
                transaction_count += 1
            
            # Random expense transactions
            if random.random() > 0.7:  # 30% chance of expense each day
                Transaction.objects.create(
                    account=random.choice(accounts[:2]),  # Use checking or savings
                    category=random.choice(expense_categories),
                    transaction_type='EXPENSE',
                    amount=Decimal(str(random.uniform(10, 200))),
                    date=trans_date,
                    description=f'Purchase on {trans_date}'
                )
                transaction_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {transaction_count} sample transactions'))
        
        # Update account balances
        for account in accounts:
            account.refresh_from_db()
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data loaded successfully!'))
        self.stdout.write(f'Total accounts: {Account.objects.count()}')
        self.stdout.write(f'Total categories: {Category.objects.count()}')
        self.stdout.write(f'Total transactions: {Transaction.objects.count()}')
