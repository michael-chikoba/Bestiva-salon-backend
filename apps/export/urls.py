from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.export_bookings, name='export-bookings'),
    path('payments/', views.export_payments, name='export-payments'),
    path('employees/', views.export_employees, name='export-employees'),
    path('customers/', views.export_customers, name='export-customers'),
]
