from django import forms
from django.forms import inlineformset_factory
from .models import MedicalRecord, Prescription, PrescriptionMedicine


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'symptoms', 'treatment', 'notes', 'follow_up_date']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acute Bronchitis, Hypertension Stage 1'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reported and observed symptoms...'}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Clinical intervention, therapy, or dietary advice...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Internal clinical notes / observations...'}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special precautions, diet recommendations, or allergy alerts...'}),
        }


class PrescriptionMedicineForm(forms.ModelForm):
    class Meta:
        model = PrescriptionMedicine
        fields = ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medicine Name (e.g. Amoxicillin)'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dosage (e.g. 500 mg)'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frequency (e.g. Twice daily)'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duration (e.g. 5 days)'}),
            'instructions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instructions (e.g. After meals)'}),
        }


PrescriptionMedicineFormSet = inlineformset_factory(
    Prescription,
    PrescriptionMedicine,
    form=PrescriptionMedicineForm,
    extra=3,
    can_delete=True
)
