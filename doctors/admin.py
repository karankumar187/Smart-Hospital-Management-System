from django.contrib import admin
from .models import Department, Doctor


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'active_doctors_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'department', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'is_available')
    list_filter = ('department', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'specialization', 'qualification')
