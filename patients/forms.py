from django import forms
from .models import Patient


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'dob',
            'gender',
            'blood_group',
            'address',
            'emergency_contact_name',
            'emergency_contact_phone',
            'medical_history',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Allergies, chronic conditions, medications'}),
        }
