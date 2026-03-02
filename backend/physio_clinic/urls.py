"""
PhysioClinic URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1 routes
    path('api/', include([
        # Auth endpoints
        path('auth/', include('physio_clinic.apps.accounts.urls')),
        # Services
        path('services/', include('physio_clinic.apps.services.urls')),
        # Appointments & availability
        path('appointments/', include('physio_clinic.apps.appointments.urls')),
        # Treatment records
        path('treatments/', include('physio_clinic.apps.treatments.urls')),
        # Notifications preferences
        path('notifications/', include('physio_clinic.apps.notifications.urls')),

        # API Schema & Docs
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
