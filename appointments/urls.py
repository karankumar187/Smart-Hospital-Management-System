from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('api/slots/', views.api_available_slots_view, name='api_available_slots'),
    path('<int:pk>/', views.appointment_detail_view, name='appointment_detail'),
    path('<int:pk>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('<int:pk>/status/', views.update_appointment_status_view, name='update_appointment_status'),
]
