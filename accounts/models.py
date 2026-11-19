from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_DOCTOR = 'DOCTOR'
    ROLE_PATIENT = 'PATIENT'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.FileField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser or self.is_staff

    @property
    def is_doctor_role(self):
        return self.role == self.ROLE_DOCTOR

    @property
    def is_patient_role(self):
        return self.role == self.ROLE_PATIENT

    def get_role_display_badge(self):
        badges = {
            self.ROLE_ADMIN: 'badge-role-admin',
            self.ROLE_DOCTOR: 'badge-role-doctor',
            self.ROLE_PATIENT: 'badge-role-patient',
        }
        return badges.get(self.role, 'badge-soft-secondary')

    def __str__(self):
        role_label = self.get_role_display()
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username} - {role_label})"
        return f"{self.username} ({role_label})"
