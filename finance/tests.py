from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .models import Account, Category, Transaction, Budget


class AccountModelTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name='Test Account',
            account_type='CHECKING',
            balance=1000.00
        )
    
    def test_account_creation(self):
        self.assertEqual(self.account.name, 'Test Account')
        self.assertEqual(self.account.balance, Decimal('1000.00'))
    
    def test_account_str(self):
        expected = f"Test Account (CHECKING) - USD 1000.00"
        self.assertEqual(str(self.account), expected)


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Groceries',
            category_type='EXPENSE'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Groceries')
        self.assertEqual(self.category.category_type, 'EXPENSE')
    
    def test_category_str(self):
        expected = "Groceries (EXPENSE)"
        self.assertEqual(str(self.category), expected)


class TransactionModelTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            name='Test Account',
            account_type='CHECKING',
            balance=1000.00
        )
        self.category = Category.objects.create(
            name='Salary',
            category_type='INCOME'
        )
    
    def test_transaction_updates_balance(self):
        initial_balance = self.account.balance
        
        # Create income transaction
        transaction = Transaction.objects.create(
            account=self.account,
            category=self.category,
            transaction_type='INCOME',
            amount=500.00,
            date=timezone.now().date()
        )
        
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, initial_balance + Decimal('500.00'))
