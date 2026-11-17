from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from accounts.decorators import patient_required
from accounts.forms import UserProfileForm
from .models import Patient
from .forms import PatientProfileForm
from appointments.models import Appointment
from records.models import MedicalRecord, Prescription


@patient_required
def patient_dashboard_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    today = date.today()

    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=today,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
    ).select_related('doctor__user', 'doctor__department').order_by('appointment_date', 'appointment_time')

    recent_records = MedicalRecord.objects.filter(
        patient=patient
    ).select_related('doctor__user', 'doctor__department').order_by('-created_at')[:4]

    recent_prescriptions = Prescription.objects.filter(
        patient=patient
    ).select_related('doctor__user', 'medical_record').order_by('-created_at')[:4]

    total_appointments = Appointment.objects.filter(patient=patient).count()
    completed_appointments = Appointment.objects.filter(patient=patient, status=Appointment.STATUS_COMPLETED).count()

    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'upcoming_count': upcoming_appointments.count(),
        'recent_records': recent_records,
        'recent_prescriptions': recent_prescriptions,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'patients/patient_dashboard.html', context)


@patient_required
def patient_profile_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        patient_form = PatientProfileForm(request.POST, instance=patient)

        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            patient_form.save()
            messages.success(request, "Your medical profile has been updated successfully.")
            return redirect('patients:patient_profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        patient_form = PatientProfileForm(instance=patient)

    context = {
        'patient': patient,
        'user_form': user_form,
        'patient_form': patient_form,
    }
    return render(request, 'patients/patient_profile.html', context)


@patient_required
def patient_appointments_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    status_filter = request.GET.get('status')

    appointments = Appointment.objects.filter(patient=patient).select_related(
        'doctor__user', 'doctor__department'
    ).order_by('-appointment_date', '-appointment_time')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    context = {
        'patient': patient,
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'patients/patient_appointments.html', context)


@patient_required
def patient_records_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    records = MedicalRecord.objects.filter(
        patient=patient
    ).select_related('doctor__user', 'doctor__department', 'appointment').order_by('-created_at')

    context = {
        'patient': patient,
        'records': records,
    }
    return render(request, 'patients/patient_records.html', context)


@patient_required
def patient_prescriptions_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    prescriptions = Prescription.objects.filter(
        patient=patient
    ).select_related('doctor__user', 'doctor__department', 'medical_record').prefetch_related('medicines').order_by('-created_at')

    context = {
        'patient': patient,
        'prescriptions': prescriptions,
    }
    return render(request, 'patients/patient_prescriptions.html', context)
