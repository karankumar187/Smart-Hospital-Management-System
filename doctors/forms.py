from django import forms
from .models import Doctor, Department


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'specialization',
            'qualification',
            'experience_years',
            'consultation_fee',
            'room_number',
            'bio',
            'working_days',
            'working_hours_start',
            'working_hours_end',
            'is_available',
        ]
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'working_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mon, Tue, Wed, Thu, Fri'}),
            'working_hours_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'working_hours_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department Overview & Services'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-heart-pulse'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
