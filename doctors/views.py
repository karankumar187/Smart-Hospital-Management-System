from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import date

from accounts.decorators import doctor_required
from accounts.forms import UserProfileForm
from .models import Doctor, Department
from .forms import DoctorProfileForm
from appointments.models import Appointment
from patients.models import Patient
from records.models import MedicalRecord


# Public views
def doctor_list_view(request):
    department_id = request.GET.get('department')
    search_query = request.GET.get('search', '').strip()

    doctors = Doctor.objects.select_related('user', 'department').filter(is_available=True)
    departments = Department.objects.filter(is_active=True)

    if department_id:
        doctors = doctors.filter(department_id=department_id)

    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search_query,
    }
    return render(request, 'doctors/doctor_list.html', context)


def doctor_detail_view(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related('user', 'department'), pk=pk)
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/doctor_detail.html', context)


def api_doctors_by_department(request):
    department_id = request.GET.get('department_id')
    if not department_id:
        doctors = Doctor.objects.filter(is_available=True)
    else:
        doctors = Doctor.objects.filter(department_id=department_id, is_available=True)

    data = [
        {
            'id': doc.id,
            'name': doc.display_name,
            'specialization': doc.specialization,
            'consultation_fee': str(doc.consultation_fee),
        }
        for doc in doctors
    ]
    return JsonResponse({'doctors': data})


# Doctor Portal (Protected)
@doctor_required
def doctor_dashboard_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    today = date.today()

    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).select_related('patient__user').order_by('appointment_time')

    pending_appointments = Appointment.objects.filter(
        doctor=doctor,
        status=Appointment.STATUS_PENDING
    ).select_related('patient__user').order_by('appointment_date', 'appointment_time')[:5]

    total_patients_count = Patient.objects.filter(appointments__doctor=doctor).distinct().count()
    completed_consultations_count = Appointment.objects.filter(doctor=doctor, status=Appointment.STATUS_COMPLETED).count()

    context = {
        'doctor': doctor,
        'today': today,
        'today_appointments': today_appointments,
        'today_appointments_count': today_appointments.count(),
        'pending_appointments': pending_appointments,
        'pending_count': Appointment.objects.filter(doctor=doctor, status=Appointment.STATUS_PENDING).count(),
        'total_patients_count': total_patients_count,
        'completed_consultations_count': completed_consultations_count,
    }
    return render(request, 'doctors/doctor_dashboard.html', context)


@doctor_required
def doctor_appointments_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')

    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user').order_by('-appointment_date', '-appointment_time')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)

    context = {
        'doctor': doctor,
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'doctors/doctor_appointments.html', context)


@doctor_required
def doctor_patients_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    search_query = request.GET.get('search', '').strip()

    patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient_id', flat=True).distinct()
    patients = Patient.objects.filter(id__in=patient_ids).select_related('user')

    if search_query:
        patients = patients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__phone__icontains=search_query)
        )

    context = {
        'doctor': doctor,
        'patients': patients,
        'search_query': search_query,
    }
    return render(request, 'doctors/doctor_patients.html', context)


@doctor_required
def doctor_patient_detail_view(request, patient_id):
    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    # Confirm relationship: doctor has an appointment with patient
    has_relationship = Appointment.objects.filter(doctor=doctor, patient=patient).exists()
    if not has_relationship and not request.user.is_admin_role:
        messages.error(request, "Access restricted. You may only view records for assigned patients.")
        return redirect('doctors:doctor_patients')

    appointments = Appointment.objects.filter(doctor=doctor, patient=patient).order_by('-appointment_date')
    medical_records = MedicalRecord.objects.filter(patient=patient, doctor=doctor).select_related('appointment').order_by('-created_at')

    context = {
        'doctor': doctor,
        'patient': patient,
        'appointments': appointments,
        'medical_records': medical_records,
    }
    return render(request, 'doctors/doctor_patient_detail.html', context)


@doctor_required
def doctor_profile_update_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        doctor_form = DoctorProfileForm(request.POST, instance=doctor)

        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            doctor_form.save()
            messages.success(request, "Your doctor profile has been updated successfully.")
            return redirect('doctors:doctor_profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        doctor_form = DoctorProfileForm(instance=doctor)

    context = {
        'doctor': doctor,
        'user_form': user_form,
        'doctor_form': doctor_form,
    }
    return render(request, 'doctors/doctor_profile.html', context)
