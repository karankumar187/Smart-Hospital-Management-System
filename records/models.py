from django.db import models


class MedicalRecord(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    diagnosis = models.TextField(help_text="Clinical diagnosis")
    symptoms = models.TextField(help_text="Presented symptoms")
    treatment = models.TextField(help_text="Recommended treatment / therapy plan")
    notes = models.TextField(blank=True, help_text="Additional doctor notes or observation")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Record #{self.id} - {self.patient} by {self.doctor} ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def has_prescription(self):
        return hasattr(self, 'prescription')


class Prescription(models.Model):
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, related_name='prescription')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    notes = models.TextField(blank=True, help_text="General instructions, lifestyle advice or precautions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient} by {self.doctor}"


class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, help_text="e.g. 500 mg, 1 tablet, 10 ml")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice daily, 1-0-1, Every 8 hours")
    duration = models.CharField(max_length=100, help_text="e.g. 5 days, 10 days, 1 month")
    instructions = models.CharField(max_length=255, blank=True, help_text="e.g. After meals with water")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} ({self.frequency})"
