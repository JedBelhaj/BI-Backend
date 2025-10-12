from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from .models import Account, Category, Transaction, Budget
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer, 
    BudgetSerializer, TransactionSummarySerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing accounts
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_active', 'currency']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all accounts"""
        accounts = self.get_queryset()
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
        active_count = accounts.filter(is_active=True).count()
        
        return Response({
            'total_balance': total_balance,
            'active_accounts': active_count,
            'total_accounts': accounts.count(),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['category_type', 'name']


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transactions
    """
    queryset = Transaction.objects.select_related('account', 'category').all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'account', 'category', 'is_recurring']
    search_fields = ['description', 'notes', 'reference']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        """Allow filtering by date range"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary"""
        queryset = self.filter_queryset(self.get_queryset())
        
        income = queryset.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        expenses = queryset.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        
        summary_data = {
            'total_income': income,
            'total_expenses': expenses,
            'net_balance': income - expenses,
            'transaction_count': queryset.count(),
        }
        
        serializer = TransactionSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get transactions grouped by category"""
        queryset = self.filter_queryset(self.get_queryset())
        
        category_summary = queryset.values(
            'category__name', 'category__id', 'transaction_type'
        ).annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('-total_amount')
        
        return Response(category_summary)
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly transaction summary for the last 12 months"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        queryset = self.get_queryset().filter(date__gte=start_date, date__lte=end_date)
        
        # Group by year-month
        from django.db.models.functions import TruncMonth
        monthly_data = queryset.annotate(
            month=TruncMonth('date')
        ).values('month', 'transaction_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        return Response(monthly_data)


class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing budgets
    """
    queryset = Budget.objects.select_related('category').all()
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['notes', 'category__name']
    ordering_fields = ['start_date', 'amount']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Allow filtering by date range"""
        queryset = super().get_queryset()
        
        # Filter for active budgets
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            today = datetime.now().date()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=today,
                end_date__gte=today
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get currently active budgets"""
        today = datetime.now().date()
        queryset = self.get_queryset().filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
