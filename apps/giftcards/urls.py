from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_gift_card, name='create-gift-card'),
    path('balance/', views.check_balance, name='check-balance'),
    path('redeem/', views.redeem_gift_card, name='redeem-gift-card'),
]
