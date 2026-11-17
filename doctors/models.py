from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-heart-pulse', help_text="Bootstrap icon name, e.g., bi-heart-pulse, bi-activity, bi-capsule")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def active_doctors_count(self):
        return self.doctors.filter(is_available=True).count()


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    specialization = models.CharField(max_length=150)
    qualification = models.CharField(max_length=150, help_text="e.g., MBBS, MD (Cardiology)")
    experience_years = models.PositiveIntegerField(default=1)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    working_days = models.CharField(max_length=150, default='Monday, Tuesday, Wednesday, Thursday, Friday')
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='17:00')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"

    @property
    def display_name(self):
        name = self.user.get_full_name()
        return f"Dr. {name}" if name else f"Dr. {self.user.username}"

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone
