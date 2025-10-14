from rest_framework import serializers
from .models import Account, Category, Transaction, Budget, BudgetData, BudgetSummary


class AccountSerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'balance', 'currency', 'description', 
                  'is_active', 'transaction_count', 'created_at', 'updated_at']
        read_only_fields = ['balance', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()


class CategorySerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'description', 'color', 'icon', 
                  'is_active', 'transaction_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'account_name', 'category', 'category_name', 
                  'transaction_type', 'amount', 'date', 'description', 'reference', 
                  'notes', 'is_recurring', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'start_date', 'end_date', 
                  'spent_amount', 'remaining_amount', 'progress_percentage', 'notes', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_spent_amount(self, obj):
        return float(obj.get_spent_amount())
    
    def get_remaining_amount(self, obj):
        return float(obj.get_remaining_amount())
    
    def get_progress_percentage(self, obj):
        spent = obj.get_spent_amount()
        if obj.amount > 0:
            return round((spent / obj.amount) * 100, 2)
        return 0
    
    def validate(self, data):
        """Ensure end_date is after start_date"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data


class BudgetDataSerializer(serializers.ModelSerializer):
    """Serializer for the new budget data schema"""
    
    class Meta:
        model = BudgetData
        fields = [
            'id', 'sheet_source', 'fiscal_year', 'processed_date', 
            'budget_category', 'budget_item', 'budget_amount', 
            'budget_description', 'department', 'account_code', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_fiscal_year(self, value):
        """Ensure fiscal year is reasonable"""
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("Fiscal year must be between 1900 and 2100.")
        return value

    def validate_budget_amount(self, value):
        """Ensure budget amount is not negative"""
        if value < 0:
            raise serializers.ValidationError("Budget amount cannot be negative.")
        return value


class BudgetSummarySerializer(serializers.ModelSerializer):
    """Serializer for budget summary statistics"""
    
    class Meta:
        model = BudgetSummary
        fields = [
            'id', 'sheet_name', 'fiscal_year', 'total_records', 
            'total_budget_amount', 'max_budget_item', 'min_budget_item', 
            'average_budget_item', 'processing_date', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_total_records(self, value):
        """Ensure total records is not negative"""
        if value < 0:
            raise serializers.ValidationError("Total records cannot be negative.")
        return value


class TransactionSummarySerializer(serializers.Serializer):
    """Serializer for transaction summaries and analytics"""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
