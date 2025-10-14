from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, CategoryViewSet, TransactionViewSet, BudgetViewSet, BudgetDataViewSet, BudgetSummaryViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'budget-data', BudgetDataViewSet, basename='budget-data')
router.register(r'budget-summary', BudgetSummaryViewSet, basename='budget-summary')

urlpatterns = [
    path('', include(router.urls)),
]
