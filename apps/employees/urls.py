from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'workers', views.WorkerViewSet, basename='worker')
router.register(r'availability', views.AvailabilityViewSet, basename='availability')

urlpatterns = [
    path('', include(router.urls)),
]
