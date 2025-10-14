from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from .models import Account, Category, Transaction, Budget, BudgetData, BudgetSummary
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer, 
    BudgetSerializer, TransactionSummarySerializer, BudgetDataSerializer, 
    BudgetSummarySerializer
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


class BudgetDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing budget data entries
    """
    queryset = BudgetData.objects.all()
    serializer_class = BudgetDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'budget_category', 'department', 'sheet_source']
    search_fields = ['budget_category', 'budget_item', 'budget_description', 'department']
    ordering_fields = ['fiscal_year', 'budget_amount', 'processed_date', 'created_at']
    ordering = ['-fiscal_year', 'budget_category', 'budget_item']
    
    def get_queryset(self):
        """Allow filtering by fiscal year range and processed date range"""
        queryset = super().get_queryset()
        
        # Filter by fiscal year range
        fiscal_year_min = self.request.query_params.get('fiscal_year_min', None)
        fiscal_year_max = self.request.query_params.get('fiscal_year_max', None)
        
        if fiscal_year_min:
            queryset = queryset.filter(fiscal_year__gte=fiscal_year_min)
        if fiscal_year_max:
            queryset = queryset.filter(fiscal_year__lte=fiscal_year_max)
        
        # Filter by processed date range
        processed_date_start = self.request.query_params.get('processed_date_start', None)
        processed_date_end = self.request.query_params.get('processed_date_end', None)
        
        if processed_date_start:
            queryset = queryset.filter(processed_date__gte=processed_date_start)
        if processed_date_end:
            queryset = queryset.filter(processed_date__lte=processed_date_end)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary_by_year(self, request):
        """Get budget summary grouped by fiscal year"""
        queryset = self.filter_queryset(self.get_queryset())
        
        yearly_summary = queryset.values('fiscal_year').annotate(
            total_budget=Sum('budget_amount'),
            record_count=Count('id'),
            category_count=Count('budget_category', distinct=True),
            department_count=Count('department', distinct=True)
        ).order_by('-fiscal_year')
        
        return Response(yearly_summary)
    
    @action(detail=False, methods=['get'])
    def summary_by_category(self, request):
        """Get budget summary grouped by category"""
        queryset = self.filter_queryset(self.get_queryset())
        
        category_summary = queryset.values(
            'budget_category', 'fiscal_year'
        ).annotate(
            total_budget=Sum('budget_amount'),
            record_count=Count('id'),
            avg_budget=Sum('budget_amount') / Count('id')
        ).order_by('-fiscal_year', '-total_budget')
        
        return Response(category_summary)
    
    @action(detail=False, methods=['get'])
    def summary_by_department(self, request):
        """Get budget summary grouped by department"""
        queryset = self.filter_queryset(self.get_queryset())
        
        department_summary = queryset.exclude(
            department__isnull=True
        ).exclude(
            department__exact=''
        ).values(
            'department', 'fiscal_year'
        ).annotate(
            total_budget=Sum('budget_amount'),
            record_count=Count('id'),
            category_count=Count('budget_category', distinct=True)
        ).order_by('-fiscal_year', '-total_budget')
        
        return Response(department_summary)


class BudgetSummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing budget summary statistics
    """
    queryset = BudgetSummary.objects.all()
    serializer_class = BudgetSummarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'sheet_name']
    search_fields = ['sheet_name']
    ordering_fields = ['fiscal_year', 'processing_date', 'total_budget_amount']
    ordering = ['-fiscal_year', '-processing_date']
    
    def get_queryset(self):
        """Allow filtering by fiscal year range"""
        queryset = super().get_queryset()
        
        # Filter by fiscal year range
        fiscal_year_min = self.request.query_params.get('fiscal_year_min', None)
        fiscal_year_max = self.request.query_params.get('fiscal_year_max', None)
        
        if fiscal_year_min:
            queryset = queryset.filter(fiscal_year__gte=fiscal_year_min)
        if fiscal_year_max:
            queryset = queryset.filter(fiscal_year__lte=fiscal_year_max)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest_by_year(self, request):
        """Get the latest summary for each fiscal year"""
        latest_summaries = []
        fiscal_years = self.get_queryset().values_list('fiscal_year', flat=True).distinct()
        
        for year in fiscal_years:
            latest = self.get_queryset().filter(fiscal_year=year).order_by('-processing_date').first()
            if latest:
                latest_summaries.append(latest)
        
        serializer = self.get_serializer(latest_summaries, many=True)
        return Response(serializer.data)
