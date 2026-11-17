"""
URL configuration for Smart Hospital Management System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('doctors/', include('doctors.urls', namespace='doctors')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('records/', include('records.urls', namespace='records')),
    path('admin-dashboard/', include('dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
