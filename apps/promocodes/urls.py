from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_promo_code, name='create-promo-code'),
    path('validate/', views.validate_promo_code, name='validate-promo-code'),
    path('apply/', views.apply_promo_code, name='apply-promo-code'),
]
