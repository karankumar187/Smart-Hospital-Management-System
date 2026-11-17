from django import forms
from datetime import date
from .models import Appointment
from doctors.models import Doctor, Department


class AppointmentBookingForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="-- All Departments --",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_department'})
    )

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_appointment_date'})
    )

    appointment_time = forms.ChoiceField(
        choices=[('', '-- Select Time Slot --')] + Appointment.TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_appointment_time'})
    )

    class Meta:
        model = Appointment
        fields = ['department', 'doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms or reason for visit...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True).select_related('user', 'department')
        self.fields['appointment_date'].widget.attrs['min'] = date.today().isoformat()

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if appt_date and appt_date < date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appt_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appt_date = cleaned_data.get('appointment_date')
        appt_time = cleaned_data.get('appointment_time')

        if doctor and appt_date and appt_time:
            # Check if conflicting appointment exists
            conflict = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appt_date,
                appointment_time=appt_time
            ).exclude(status__in=[Appointment.STATUS_CANCELLED, Appointment.STATUS_REJECTED]).exists()

            if conflict:
                raise forms.ValidationError("This time slot is already booked for this doctor. Please choose a different time or doctor.")

        return cleaned_data


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'doctor_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional internal or patient note'}),
        }


class AppointmentCancelForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['cancellation_reason']
        widgets = {
            'cancellation_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for cancellation...'}),
        }
