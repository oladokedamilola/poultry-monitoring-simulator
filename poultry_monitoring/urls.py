# poultry_monitoring/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import home
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitoring.urls')),  # For API endpoints
    path('m/', include('monitoring.urls')),     # For web views
    path("users/", include("users.urls")),
    path("flock/", include("flock.urls")),
    path('', home, name='home'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)