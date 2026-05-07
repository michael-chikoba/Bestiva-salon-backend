# apps/inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # List and create items
    path('', views.list_inventory, name='list-inventory'),
    
    # Add new item
    path('add/', views.add_inventory_item, name='add-inventory'),
    
    # Low stock alerts
    path('low-stock/', views.low_stock_alerts, name='low-stock'),
    
    # Inventory statistics
    path('stats/', views.inventory_stats, name='inventory-stats'),
    
    # Item detail (retrieve, update, delete)
    path('<int:pk>/', views.inventory_detail, name='inventory-detail'),
    
    # Restock an item
    path('<int:pk>/restock/', views.restock_item, name='restock-item'),
    
    # Item transactions
    path('<int:pk>/transactions/', views.inventory_transactions, name='item-transactions'),
    
    # All transactions
    path('transactions/', views.inventory_transactions, name='all-transactions'),
]