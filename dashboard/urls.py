from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),

    # Doctors
    path('doctors/', views.admin_doctors_list_view, name='admin_doctors_list'),
    path('doctors/create/', views.admin_doctor_create_view, name='admin_doctor_create'),
    path('doctors/<int:pk>/edit/', views.admin_doctor_edit_view, name='admin_doctor_edit'),
    path('doctors/<int:pk>/toggle-status/', views.admin_doctor_toggle_status_view, name='admin_doctor_toggle_status'),
    path('doctors/<int:pk>/delete/', views.admin_doctor_delete_view, name='admin_doctor_delete'),

    # Patients
    path('patients/', views.admin_patients_list_view, name='admin_patients_list'),
    path('patients/<int:pk>/edit/', views.admin_patient_edit_view, name='admin_patient_edit'),
    path('patients/<int:pk>/delete/', views.admin_patient_delete_view, name='admin_patient_delete'),

    # Departments
    path('departments/', views.admin_departments_list_view, name='admin_departments_list'),
    path('departments/create/', views.admin_department_create_view, name='admin_department_create'),
    path('departments/<int:pk>/edit/', views.admin_department_edit_view, name='admin_department_edit'),
    path('departments/<int:pk>/delete/', views.admin_department_delete_view, name='admin_department_delete'),

    # Appointments
    path('appointments/', views.admin_appointments_list_view, name='admin_appointments'),

    # Records
    path('records/', views.admin_records_list_view, name='admin_records'),
]
