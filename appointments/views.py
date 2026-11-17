from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date

from accounts.decorators import patient_required, role_required
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentStatusForm, AppointmentCancelForm
from patients.models import Patient
from doctors.models import Doctor


@patient_required
def book_appointment_view(request):
    patient, _ = Patient.objects.get_or_create(user=request.user)
    doctor_id = request.GET.get('doctor')
    initial_data = {}

    if doctor_id:
        try:
            doc = Doctor.objects.get(id=doctor_id, is_available=True)
            initial_data['doctor'] = doc
            if doc.department:
                initial_data['department'] = doc.department
        except Doctor.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.status = Appointment.STATUS_PENDING
            appointment.save()
            messages.success(
                request,
                f"Your appointment request with {appointment.doctor} for {appointment.appointment_date} has been submitted! Status: Pending confirmation."
            )
            return redirect('patients:patient_appointments')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = AppointmentBookingForm(initial=initial_data)

    context = {
        'form': form,
        'patient': patient,
        'all_slots': Appointment.TIME_SLOT_CHOICES,
    }
    return render(request, 'appointments/book_appointment.html', context)


def api_available_slots_view(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'doctor_id and date are required.'}, status=400)

    booked_times = Appointment.objects.filter(
        doctor_id=doctor_id,
        appointment_date=date_str
    ).exclude(
        status__in=[Appointment.STATUS_CANCELLED, Appointment.STATUS_REJECTED]
    ).values_list('appointment_time', flat=True)

    booked_formatted = [t.strftime('%H:%M:%S') for t in booked_times]

    slots_data = []
    for val, label in Appointment.TIME_SLOT_CHOICES:
        slots_data.append({
            'value': val,
            'label': label,
            'is_booked': val in booked_formatted
        })

    return JsonResponse({'slots': slots_data})


@login_required
def appointment_detail_view(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__department'),
        pk=pk
    )

    # Permission check: must be the patient, the doctor, or an admin
    user = request.user
    is_patient_owner = hasattr(user, 'patient_profile') and appointment.patient == user.patient_profile
    is_doctor_owner = hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_patient_owner or is_doctor_owner or is_admin):
        messages.error(request, "You are not authorized to view this appointment.")
        return redirect('accounts:dashboard_redirect')

    context = {
        'appointment': appointment,
        'is_patient_owner': is_patient_owner,
        'is_doctor_owner': is_doctor_owner,
        'is_admin': is_admin,
        'has_record': hasattr(appointment, 'medical_record'),
    }
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def cancel_appointment_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    is_patient_owner = hasattr(user, 'patient_profile') and appointment.patient == user.patient_profile
    is_doctor_owner = hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_patient_owner or is_doctor_owner or is_admin):
        messages.error(request, "Permission denied.")
        return redirect('accounts:dashboard_redirect')

    if appointment.status in [Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED]:
        messages.warning(request, f"This appointment cannot be cancelled because it is already {appointment.status}.")
        return redirect('appointments:appointment_detail', pk=pk)

    if request.method == 'POST':
        form = AppointmentCancelForm(request.POST, instance=appointment)
        if form.is_valid():
            cancelled_appt = form.save(commit=False)
            cancelled_appt.status = Appointment.STATUS_CANCELLED
            cancelled_appt.save()
            messages.success(request, "The appointment has been cancelled.")
            if is_patient_owner:
                return redirect('patients:patient_appointments')
            elif is_doctor_owner:
                return redirect('doctors:doctor_appointments')
            else:
                return redirect('dashboard:admin_appointments')
    else:
        form = AppointmentCancelForm(instance=appointment)

    context = {
        'appointment': appointment,
        'form': form,
    }
    return render(request, 'appointments/cancel_appointment.html', context)


@login_required
def update_appointment_status_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    is_doctor_owner = hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile
    is_admin = user.is_admin_role

    if not (is_doctor_owner or is_admin):
        messages.error(request, "Only the assigned doctor or administrator can update the appointment status.")
        return redirect('appointments:appointment_detail', pk=pk)

    new_status = request.GET.get('status')
    if new_status and new_status in dict(Appointment.STATUS_CHOICES):
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment status updated to '{new_status}'.")
        if is_doctor_owner:
            return redirect('doctors:doctor_appointments')
        return redirect('dashboard:admin_appointments')

    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Appointment #{appointment.id} updated successfully.")
            if is_doctor_owner:
                return redirect('doctors:doctor_appointments')
            return redirect('dashboard:admin_appointments')
    else:
        form = AppointmentStatusForm(instance=appointment)

    context = {
        'appointment': appointment,
        'form': form,
    }
    return render(request, 'appointments/appointment_status_update.html', context)
