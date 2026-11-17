from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import User
from doctors.models import Doctor, Department
from patients.models import Patient
from appointments.models import Appointment

User = get_user_model()


class AdminDoctorCreateForm(forms.Form):
    # User Account Details
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # Doctor Profile Details
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    specialization = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Interventional Cardiologist'}))
    qualification = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD, DM'}))
    experience_years = forms.IntegerField(min_value=0, initial=5, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, initial=50.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    room_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room 204, 2nd Floor'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    working_days = forms.CharField(initial='Monday, Tuesday, Wednesday, Thursday, Friday', widget=forms.TextInput(attrs={'class': 'form-control'}))
    working_hours_start = forms.TimeField(initial='09:00', widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    working_hours_end = forms.TimeField(initial='17:00', widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    is_available = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password'],
            phone=self.cleaned_data.get('phone', ''),
            role=User.ROLE_DOCTOR
        )
        doctor = Doctor.objects.create(
            user=user,
            department=self.cleaned_data.get('department'),
            specialization=self.cleaned_data['specialization'],
            qualification=self.cleaned_data['qualification'],
            experience_years=self.cleaned_data['experience_years'],
            consultation_fee=self.cleaned_data['consultation_fee'],
            room_number=self.cleaned_data.get('room_number', ''),
            bio=self.cleaned_data.get('bio', ''),
            working_days=self.cleaned_data.get('working_days', 'Monday - Friday'),
            working_hours_start=self.cleaned_data.get('working_hours_start', '09:00'),
            working_hours_end=self.cleaned_data.get('working_hours_end', '17:00'),
            is_available=self.cleaned_data.get('is_available', True)
        )
        return doctor


class AdminPatientEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Patient
        fields = ['dob', 'gender', 'blood_group', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'medical_history']
        widgets = {
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        patient = super().save(commit=False)
        user = patient.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
            patient.save()
        return patient
