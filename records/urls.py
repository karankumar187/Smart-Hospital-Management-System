from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('consultation/<int:appointment_id>/', views.create_consultation_record_view, name='create_consultation_record'),
    path('<int:pk>/', views.medical_record_detail_view, name='medical_record_detail'),
    path('prescriptions/<int:pk>/', views.prescription_detail_view, name='prescription_detail'),
    path('prescriptions/<int:pk>/print/', views.prescription_print_view, name='prescription_print'),
]
