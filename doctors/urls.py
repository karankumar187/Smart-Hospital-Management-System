from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # Public
    path('', views.doctor_list_view, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail_view, name='doctor_detail'),
    path('api/by-department/', views.api_doctors_by_department, name='api_doctors_by_department'),

    # Doctor Portal
    path('portal/dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('portal/appointments/', views.doctor_appointments_view, name='doctor_appointments'),
    path('portal/patients/', views.doctor_patients_view, name='doctor_patients'),
    path('portal/patients/<int:patient_id>/', views.doctor_patient_detail_view, name='doctor_patient_detail'),
    path('portal/profile/', views.doctor_profile_update_view, name='doctor_profile'),
]
