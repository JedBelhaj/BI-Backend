from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class BudgetData(models.Model):
    """Main budget data table matching the PostgreSQL schema"""
    
    sheet_source = models.CharField(max_length=255, help_text="Source of the budget data (Excel sheet, etc.)")
    fiscal_year = models.IntegerField(help_text="Fiscal year for this budget item")
    processed_date = models.DateField(help_text="Date when this data was processed")
    budget_category = models.CharField(max_length=255, help_text="Main budget category")
    budget_item = models.CharField(max_length=255, help_text="Specific budget item")
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Budget amount")
    budget_description = models.TextField(blank=True, help_text="Detailed description of the budget item")
    department = models.CharField(max_length=255, blank=True, help_text="Department responsible for this budget")
    account_code = models.CharField(max_length=100, blank=True, help_text="Internal account code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fiscal_year', 'budget_category', 'budget_item']
        verbose_name = "Budget Data"
        verbose_name_plural = "Budget Data"
        indexes = [
            models.Index(fields=['fiscal_year']),
            models.Index(fields=['budget_category']),
            models.Index(fields=['department']),
            models.Index(fields=['processed_date']),
        ]

    def __str__(self):
        return f"{self.budget_category} - {self.budget_item} ({self.fiscal_year})"


class BudgetSummary(models.Model):
    """Budget summary table for aggregated statistics"""
    
    sheet_name = models.CharField(max_length=255, help_text="Name of the source sheet")
    fiscal_year = models.IntegerField(help_text="Fiscal year for this summary")
    total_records = models.IntegerField(help_text="Total number of budget records processed")
    total_budget_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total budget amount")
    max_budget_item = models.DecimalField(max_digits=15, decimal_places=2, help_text="Maximum budget item amount")
    min_budget_item = models.DecimalField(max_digits=15, decimal_places=2, help_text="Minimum budget item amount")
    average_budget_item = models.DecimalField(max_digits=15, decimal_places=2, help_text="Average budget item amount")
    processing_date = models.DateTimeField(help_text="When this summary was generated")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fiscal_year', '-processing_date']
        verbose_name = "Budget Summary"
        verbose_name_plural = "Budget Summaries"
        unique_together = ['sheet_name', 'fiscal_year']
        indexes = [
            models.Index(fields=['fiscal_year']),
            models.Index(fields=['processing_date']),
        ]

    def __str__(self):
        return f"{self.sheet_name} Summary - FY{self.fiscal_year} ({self.total_records} records)"


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
