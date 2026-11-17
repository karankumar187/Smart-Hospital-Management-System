from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, datetime


class Appointment(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'
    STATUS_REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00:00', '09:00 AM'),
        ('09:30:00', '09:30 AM'),
        ('10:00:00', '10:00 AM'),
        ('10:30:00', '10:30 AM'),
        ('11:00:00', '11:00 AM'),
        ('11:30:00', '11:30 AM'),
        ('12:00:00', '12:00 PM'),
        ('12:30:00', '12:30 PM'),
        ('14:00:00', '02:00 PM'),
        ('14:30:00', '02:30 PM'),
        ('15:00:00', '03:00 PM'),
        ('15:30:00', '03:30 PM'),
        ('16:00:00', '04:00 PM'),
        ('16:30:00', '04:30 PM'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reason = models.TextField(help_text="Primary complaint or symptoms")
    doctor_notes = models.TextField(blank=True, help_text="Notes from doctor or receptionist")
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'appointment_time'],
                condition=~models.Q(status__in=['Cancelled', 'Rejected']),
                name='unique_active_doctor_appointment'
            )
        ]

    def clean(self):
        super().clean()
        if self.appointment_date and self.appointment_date < date.today():
            raise ValidationError({'appointment_date': "Appointment date cannot be in the past."})

        # Prevent duplicate active appointment for the doctor at the same slot
        if self.doctor_id and self.appointment_date and self.appointment_time:
            conflicts = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time
            ).exclude(status__in=[self.STATUS_CANCELLED, self.STATUS_REJECTED])

            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)

            if conflicts.exists():
                raise ValidationError("This doctor already has a booked appointment at this date and time.")

    def get_status_badge(self):
        badges = {
            self.STATUS_PENDING: 'bg-warning text-dark',
            self.STATUS_CONFIRMED: 'bg-primary',
            self.STATUS_COMPLETED: 'bg-success',
            self.STATUS_CANCELLED: 'bg-danger',
            self.STATUS_REJECTED: 'bg-secondary',
        }
        return badges.get(self.status, 'bg-secondary')

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date} at {self.appointment_time} ({self.status})"
