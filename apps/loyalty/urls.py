from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.LoyaltyTransactionViewSet, basename='loyalty-transaction')
router.register(r'rewards', views.RewardViewSet, basename='reward')

urlpatterns = [
    path('', include(router.urls)),
]
