from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Account(models.Model):
    """Represents a financial account (e.g., Bank Account, Credit Card, Cash)"""
    ACCOUNT_TYPES = [
        ('CHECKING', 'Checking Account'),
        ('SAVINGS', 'Savings Account'),
        ('CREDIT', 'Credit Card'),
        ('CASH', 'Cash'),
        ('INVESTMENT', 'Investment Account'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='CHECKING')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.account_type}) - {self.currency} {self.balance}"


class Category(models.Model):
    """Represents a transaction category (e.g., Food, Transport, Salary)"""
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#0066cc', help_text='Hex color code')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text='Icon identifier')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category_type', 'name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Transaction(models.Model):
    """Represents a financial transaction"""
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True, help_text='Reference number or ID')
    notes = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['account']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.transaction_type} - {self.amount} ({self.account.name})"
    
    def save(self, *args, **kwargs):
        """Update account balance when transaction is saved"""
        is_new = self.pk is None
        
        if not is_new:
            # If updating, revert the old transaction effect first
            old_transaction = Transaction.objects.get(pk=self.pk)
            if old_transaction.transaction_type == 'INCOME':
                old_transaction.account.balance -= old_transaction.amount
            elif old_transaction.transaction_type == 'EXPENSE':
                old_transaction.account.balance += old_transaction.amount
            old_transaction.account.save()
        
        # Apply the new transaction
        if self.transaction_type == 'INCOME':
            self.account.balance += self.amount
        elif self.transaction_type == 'EXPENSE':
            self.account.balance -= self.amount
        
        self.account.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Update account balance when transaction is deleted"""
        if self.transaction_type == 'INCOME':
            self.account.balance -= self.amount
        elif self.transaction_type == 'EXPENSE':
            self.account.balance += self.amount
        self.account.save()
        super().delete(*args, **kwargs)


class Budget(models.Model):
    """Represents a budget for a specific category and time period"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.start_date} to {self.end_date})"
    
    def get_spent_amount(self):
        """Calculate how much has been spent in this budget period"""
        transactions = Transaction.objects.filter(
            category=self.category,
            transaction_type='EXPENSE',
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        return sum(t.amount for t in transactions)
    
    def get_remaining_amount(self):
        """Calculate remaining budget"""
        return self.amount - self.get_spent_amount()
