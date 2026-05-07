"""
apps/analytics/urls.py

Mount this in your root urls.py:
    path("api/analytics/", include("apps.analytics.urls")),
"""

from django.urls import path
from .views import (
    AnalyticsMetricsView,
    RevenueTrendView,
    TopServicesView,
    StaffPerformanceView,
)

urlpatterns = [
    path("metrics/",           AnalyticsMetricsView.as_view(),    name="analytics-metrics"),
    path("revenue-trend/",     RevenueTrendView.as_view(),         name="analytics-revenue-trend"),
    path("top-services/",      TopServicesView.as_view(),          name="analytics-top-services"),
    path("staff-performance/", StaffPerformanceView.as_view(),     name="analytics-staff-performance"),
]