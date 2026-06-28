from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API v1 endpoints
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/drivers/', include('apps.drivers.urls')),
    path('api/v1/cars/', include('apps.cars.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/earnings/', include('apps.earnings.urls')),
    path('api/v1/expenses/', include('apps.expenses.urls')),
    path('api/v1/advances/', include('apps.advances.urls')),
    path('api/v1/settlements/', include('apps.settlements.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
