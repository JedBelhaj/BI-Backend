from django.contrib import admin
from .models import Account, Category, Transaction, Budget, BudgetData, BudgetSummary


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'balance', 'currency', 'is_active', 'created_at']
    list_filter = ['account_type', 'is_active', 'currency']
    search_fields = ['name', 'description']
    readonly_fields = ['balance', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'account_type', 'currency', 'description')
        }),
        ('Status', {
            'fields': ('balance', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'color', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category_type', 'description')
        }),
        ('Appearance', {
            'fields': ('color', 'icon')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'account', 'transaction_type', 'category', 'amount', 'description', 'created_at']
    list_filter = ['transaction_type', 'account', 'category', 'date', 'is_recurring']
    search_fields = ['description', 'notes', 'reference']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['account', 'category']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('account', 'transaction_type', 'category', 'amount', 'date')
        }),
        ('Additional Information', {
            'fields': ('description', 'reference', 'notes', 'is_recurring')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('account', 'category')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'start_date', 'end_date', 'get_spent', 'get_remaining', 'is_active']
    list_filter = ['is_active', 'category', 'start_date']
    search_fields = ['category__name', 'notes']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at', 'get_spent', 'get_remaining']
    autocomplete_fields = ['category']
    fieldsets = (
        ('Budget Information', {
            'fields': ('category', 'amount', 'start_date', 'end_date')
        }),
        ('Budget Status', {
            'fields': ('get_spent', 'get_remaining', 'is_active')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_spent(self, obj):
        """Display spent amount"""
        return f"${obj.get_spent_amount():.2f}"
    get_spent.short_description = 'Spent'
    
    def get_remaining(self, obj):
        """Display remaining amount"""
        remaining = obj.get_remaining_amount()
        return f"${remaining:.2f}"
    get_remaining.short_description = 'Remaining'


@admin.register(BudgetData)
class BudgetDataAdmin(admin.ModelAdmin):
    list_display = [
        'fiscal_year', 'budget_category', 'budget_item', 'budget_amount', 
        'department', 'sheet_source', 'processed_date', 'created_at'
    ]
    list_filter = [
        'fiscal_year', 'budget_category', 'department', 'sheet_source', 'processed_date'
    ]
    search_fields = [
        'budget_category', 'budget_item', 'budget_description', 'department', 'account_code'
    ]
    date_hierarchy = 'processed_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Budget Information', {
            'fields': (
                'sheet_source', 'fiscal_year', 'processed_date', 
                'budget_category', 'budget_item', 'budget_amount'
            )
        }),
        ('Details', {
            'fields': ('budget_description', 'department', 'account_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add filters for better navigation
    list_per_page = 50
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).order_by('-fiscal_year', 'budget_category', 'budget_item')


@admin.register(BudgetSummary)
class BudgetSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'fiscal_year', 'sheet_name', 'total_records', 'total_budget_amount', 
        'processing_date', 'created_at'
    ]
    list_filter = ['fiscal_year', 'sheet_name', 'processing_date']
    search_fields = ['sheet_name']
    date_hierarchy = 'processing_date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Summary Information', {
            'fields': ('sheet_name', 'fiscal_year', 'processing_date')
        }),
        ('Statistics', {
            'fields': (
                'total_records', 'total_budget_amount', 
                'max_budget_item', 'min_budget_item', 'average_budget_item'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Add custom display methods
    def get_total_budget_display(self, obj):
        """Format total budget amount"""
        return f"${obj.total_budget_amount:,.2f}"
    get_total_budget_display.short_description = 'Total Budget'
    
    def get_records_display(self, obj):
        """Display record count"""
        return f"{obj.total_records:,} records"
    get_records_display.short_description = 'Records'


# Customize admin site headers
admin.site.site_header = "Budget Management Admin"
admin.site.site_title = "Budget Admin"
admin.site.index_title = "Welcome to Budget Management System"
