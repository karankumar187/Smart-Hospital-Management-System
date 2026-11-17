from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('profile/', views.patient_profile_view, name='patient_profile'),
    path('appointments/', views.patient_appointments_view, name='patient_appointments'),
    path('records/', views.patient_records_view, name='patient_records'),
    path('prescriptions/', views.patient_prescriptions_view, name='patient_prescriptions'),
]
