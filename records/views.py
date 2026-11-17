from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied

from accounts.decorators import doctor_required
from .models import MedicalRecord, Prescription, PrescriptionMedicine
from .forms import MedicalRecordForm, PrescriptionForm, PrescriptionMedicineFormSet
from appointments.models import Appointment
from patients.models import Patient
from doctors.models import Doctor


@login_required
def create_consultation_record_view(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__department'),
        pk=appointment_id
    )
    user = request.user

    # Only the assigned doctor or admin can create records
    is_assigned_doctor = hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile
    if not (is_assigned_doctor or user.is_admin_role):
        messages.error(request, "Only the assigned doctor can add medical consultation records.")
        return redirect('appointments:appointment_detail', pk=appointment_id)

    # Check if record already exists for this appointment
    if hasattr(appointment, 'medical_record'):
        messages.info(request, "A medical record already exists for this appointment.")
        return redirect('records:medical_record_detail', pk=appointment.medical_record.pk)

    if request.method == 'POST':
        record_form = MedicalRecordForm(request.POST)
        prescription_form = PrescriptionForm(request.POST)
        medicine_formset = PrescriptionMedicineFormSet(request.POST)

        if record_form.is_valid() and prescription_form.is_valid() and medicine_formset.is_valid():
            with transaction.atomic():
                medical_record = record_form.save(commit=False)
                medical_record.patient = appointment.patient
                medical_record.doctor = appointment.doctor
                medical_record.appointment = appointment
                medical_record.save()

                # Mark appointment completed
                appointment.status = Appointment.STATUS_COMPLETED
                appointment.save()

                # Check if medicines were submitted or prescription notes provided
                has_medicines = any(
                    form.cleaned_data.get('medicine_name')
                    for form in medicine_formset.forms
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                )
                rx_notes = prescription_form.cleaned_data.get('notes', '').strip()

                if has_medicines or rx_notes:
                    prescription = prescription_form.save(commit=False)
                    prescription.medical_record = medical_record
                    prescription.patient = appointment.patient
                    prescription.doctor = appointment.doctor
                    prescription.save()

                    # Save medicines
                    medicine_formset.instance = prescription
                    medicine_formset.save()

            messages.success(request, f"Consultation record and prescription created successfully for {appointment.patient.display_name}!")
            return redirect('records:medical_record_detail', pk=medical_record.pk)
        else:
            messages.error(request, "Please review the errors in the consultation form.")
    else:
        record_form = MedicalRecordForm()
        prescription_form = PrescriptionForm()
        medicine_formset = PrescriptionMedicineFormSet()

    context = {
        'appointment': appointment,
        'record_form': record_form,
        'prescription_form': prescription_form,
        'medicine_formset': medicine_formset,
    }
    return render(request, 'records/create_consultation_record.html', context)


@login_required
def medical_record_detail_view(request, pk):
    record = get_object_or_404(
        MedicalRecord.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__department', 'appointment'
        ),
        pk=pk
    )
    user = request.user

    is_patient_owner = hasattr(user, 'patient_profile') and record.patient == user.patient_profile
    is_doctor_owner = hasattr(user, 'doctor_profile') and record.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_patient_owner or is_doctor_owner or is_admin):
        messages.error(request, "You do not have permission to view this medical record.")
        return redirect('accounts:dashboard_redirect')

    context = {
        'record': record,
        'has_prescription': hasattr(record, 'prescription'),
        'is_patient_owner': is_patient_owner,
        'is_doctor_owner': is_doctor_owner,
    }
    return render(request, 'records/medical_record_detail.html', context)


@login_required
def prescription_detail_view(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__department', 'medical_record'
        ).prefetch_related('medicines'),
        pk=pk
    )
    user = request.user

    is_patient_owner = hasattr(user, 'patient_profile') and prescription.patient == user.patient_profile
    is_doctor_owner = hasattr(user, 'doctor_profile') and prescription.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_patient_owner or is_doctor_owner or is_admin):
        messages.error(request, "You do not have permission to view this prescription.")
        return redirect('accounts:dashboard_redirect')

    context = {
        'prescription': prescription,
        'medicines': prescription.medicines.all(),
        'is_patient_owner': is_patient_owner,
        'is_doctor_owner': is_doctor_owner,
    }
    return render(request, 'records/prescription_detail.html', context)


@login_required
def prescription_print_view(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__department', 'medical_record'
        ).prefetch_related('medicines'),
        pk=pk
    )
    user = request.user

    is_patient_owner = hasattr(user, 'patient_profile') and prescription.patient == user.patient_profile
    is_doctor_owner = hasattr(user, 'doctor_profile') and prescription.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_patient_owner or is_doctor_owner or is_admin):
        messages.error(request, "Permission denied.")
        return redirect('accounts:dashboard_redirect')

    context = {
        'prescription': prescription,
        'medicines': prescription.medicines.all(),
    }
    return render(request, 'records/prescription_print.html', context)
