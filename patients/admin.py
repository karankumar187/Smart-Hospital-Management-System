from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'gender', 'dob', 'blood_group', 'emergency_contact_phone', 'created_at')
    list_filter = ('gender', 'blood_group')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user__email', 'emergency_contact_name')
