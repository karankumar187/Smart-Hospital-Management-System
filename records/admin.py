from django.contrib import admin
from .models import MedicalRecord, Prescription, PrescriptionMedicine


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'created_at')
    inlines = [PrescriptionMedicineInline]
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'diagnosis', 'follow_up_date', 'created_at')
    list_filter = ('created_at', 'doctor__department')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'diagnosis', 'symptoms')


@admin.register(PrescriptionMedicine)
class PrescriptionMedicineAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'dosage', 'frequency', 'duration', 'prescription')
    search_fields = ('medicine_name',)
