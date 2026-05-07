from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'message': 'Welcome to SalonPro API',
        'version': '1.0.0',
        'status': 'running',
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/bookings/', include('apps.bookings.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/loyalty/', include('apps.loyalty.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/export/', include('apps.export.urls')),
    path('api/waitlist/', include('apps.waitlist.urls')),
    path('api/gift-cards/', include('apps.giftcards.urls')),
    path('api/promo-codes/', include('apps.promocodes.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/settings/', include('apps.settings.urls')),
]
