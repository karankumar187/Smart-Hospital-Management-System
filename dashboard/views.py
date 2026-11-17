import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date, timedelta

from accounts.decorators import admin_required
from accounts.models import User
from doctors.models import Doctor, Department
from doctors.forms import DoctorProfileForm, DepartmentForm
from patients.models import Patient
from appointments.models import Appointment
from appointments.forms import AppointmentStatusForm
from records.models import MedicalRecord, Prescription
from .forms import AdminDoctorCreateForm, AdminPatientEditForm


@admin_required
def admin_dashboard_view(request):
    today = date.today()

    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_departments = Department.objects.count()
    total_appointments = Appointment.objects.count()

    pending_appointments = Appointment.objects.filter(status=Appointment.STATUS_PENDING).count()
    completed_appointments = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count()
    confirmed_appointments = Appointment.objects.filter(status=Appointment.STATUS_CONFIRMED).count()
    cancelled_appointments = Appointment.objects.filter(status=Appointment.STATUS_CANCELLED).count()
    rejected_appointments = Appointment.objects.filter(status=Appointment.STATUS_REJECTED).count()

    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    total_records = MedicalRecord.objects.count()

    recent_appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user', 'doctor__department'
    ).order_by('-created_at')[:8]

    # Chart 1: Status Distribution
    status_labels = ['Pending', 'Confirmed', 'Completed', 'Cancelled', 'Rejected']
    status_counts = [
        pending_appointments,
        confirmed_appointments,
        completed_appointments,
        cancelled_appointments,
        rejected_appointments
    ]

    # Chart 2: Department-wise appointments
    dept_stats = Department.objects.annotate(
        appointment_count=Count('doctors__appointments')
    ).values('name', 'appointment_count')

    dept_labels = [d['name'] for d in dept_stats]
    dept_counts = [d['appointment_count'] for d in dept_stats]

    # Chart 3: Last 7 Days trend
    trend_labels = []
    trend_counts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%b %d')
        cnt = Appointment.objects.filter(appointment_date=day).count()
        trend_labels.append(day_str)
        trend_counts.append(cnt)

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'today_appointments': today_appointments,
        'total_records': total_records,
        'recent_appointments': recent_appointments,

        # Chart JSON
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'dept_labels_json': json.dumps(dept_labels),
        'dept_counts_json': json.dumps(dept_counts),
        'trend_labels_json': json.dumps(trend_labels),
        'trend_counts_json': json.dumps(trend_counts),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# Doctors Management
@admin_required
def admin_doctors_list_view(request):
    department_id = request.GET.get('department')
    search_query = request.GET.get('search', '').strip()

    doctors = Doctor.objects.select_related('user', 'department').all()
    departments = Department.objects.all()

    if department_id:
        doctors = doctors.filter(department_id=department_id)

    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search_query,
    }
    return render(request, 'dashboard/doctors_list.html', context)


@admin_required
def admin_doctor_create_view(request):
    if request.method == 'POST':
        form = AdminDoctorCreateForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor account '{doctor.display_name}' created successfully.")
            return redirect('dashboard:admin_doctors_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminDoctorCreateForm()

    return render(request, 'dashboard/doctor_create.html', {'form': form})


@admin_required
def admin_doctor_edit_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    user = doctor.user

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        phone = request.POST.get('phone', user.phone)
        dept_id = request.POST.get('department')

        if form.is_valid():
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.save()

            doc_inst = form.save(commit=False)
            if dept_id:
                doc_inst.department_id = dept_id
            doc_inst.save()

            messages.success(request, f"Doctor profile for {doctor.display_name} updated successfully.")
            return redirect('dashboard:admin_doctors_list')
    else:
        form = DoctorProfileForm(instance=doctor)

    departments = Department.objects.all()
    context = {
        'doctor': doctor,
        'form': form,
        'departments': departments,
    }
    return render(request, 'dashboard/doctor_edit.html', context)


@admin_required
def admin_doctor_toggle_status_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.is_available = not doctor.is_available
    doctor.save()
    status_str = "Available" if doctor.is_available else "Unavailable"
    messages.success(request, f"{doctor.display_name} is now marked as {status_str}.")
    return redirect('dashboard:admin_doctors_list')


@admin_required
def admin_doctor_delete_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    user = doctor.user
    if request.method == 'POST':
        doc_name = doctor.display_name
        user.delete()  # Cascade deletes Doctor
        messages.success(request, f"Doctor {doc_name} deleted successfully.")
        return redirect('dashboard:admin_doctors_list')

    return render(request, 'dashboard/doctor_confirm_delete.html', {'doctor': doctor})


# Patients Management
@admin_required
def admin_patients_list_view(request):
    search_query = request.GET.get('search', '').strip()
    blood_group = request.GET.get('blood_group')

    patients = Patient.objects.select_related('user').all()

    if search_query:
        patients = patients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__phone__icontains=search_query)
        )

    if blood_group:
        patients = patients.filter(blood_group=blood_group)

    context = {
        'patients': patients,
        'search_query': search_query,
        'blood_group': blood_group,
        'blood_groups': Patient.BLOOD_GROUP_CHOICES,
    }
    return render(request, 'dashboard/patients_list.html', context)


@admin_required
def admin_patient_edit_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = AdminPatientEditForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient {patient.display_name} updated successfully.")
            return redirect('dashboard:admin_patients_list')
    else:
        form = AdminPatientEditForm(instance=patient)

    return render(request, 'dashboard/patient_edit.html', {'patient': patient, 'form': form})


@admin_required
def admin_patient_delete_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    user = patient.user
    if request.method == 'POST':
        pname = patient.display_name
        user.delete()
        messages.success(request, f"Patient {pname} deleted successfully.")
        return redirect('dashboard:admin_patients_list')

    return render(request, 'dashboard/patient_confirm_delete.html', {'patient': patient})


# Departments Management
@admin_required
def admin_departments_list_view(request):
    departments = Department.objects.annotate(
        doctors_count=Count('doctors'),
        appointments_count=Count('doctors__appointments')
    ).all()

    context = {
        'departments': departments,
    }
    return render(request, 'dashboard/departments_list.html', context)


@admin_required
def admin_department_create_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully.")
            return redirect('dashboard:admin_departments_list')
    else:
        form = DepartmentForm()

    return render(request, 'dashboard/department_form.html', {'form': form, 'title': 'Add New Department'})


@admin_required
def admin_department_edit_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully.")
            return redirect('dashboard:admin_departments_list')
    else:
        form = DepartmentForm(instance=dept)

    return render(request, 'dashboard/department_form.html', {'form': form, 'department': dept, 'title': f'Edit Department: {dept.name}'})


@admin_required
def admin_department_delete_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dname = dept.name
        dept.delete()
        messages.success(request, f"Department '{dname}' removed successfully.")
        return redirect('dashboard:admin_departments_list')

    return render(request, 'dashboard/department_confirm_delete.html', {'department': dept})


# Appointments Management
@admin_required
def admin_appointments_list_view(request):
    status_filter = request.GET.get('status')
    department_id = request.GET.get('department')
    date_filter = request.GET.get('date')
    search_query = request.GET.get('search', '').strip()

    appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user', 'doctor__department'
    ).order_by('-appointment_date', '-appointment_time')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if department_id:
        appointments = appointments.filter(doctor__department_id=department_id)

    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)

    if search_query:
        appointments = appointments.filter(
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(doctor__user__last_name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'department_id': department_id,
        'date_filter': date_filter,
        'search_query': search_query,
        'departments': Department.objects.all(),
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'dashboard/appointments_list.html', context)


# Medical Records & Prescriptions
@admin_required
def admin_records_list_view(request):
    search_query = request.GET.get('search', '').strip()

    records = MedicalRecord.objects.select_related(
        'patient__user', 'doctor__user', 'doctor__department', 'appointment'
    ).order_by('-created_at')

    if search_query:
        records = records.filter(
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(doctor__user__first_name__icontains=search_query) |
            Q(diagnosis__icontains=search_query)
        )

    context = {
        'records': records,
        'search_query': search_query,
    }
    return render(request, 'dashboard/records_list.html', context)
