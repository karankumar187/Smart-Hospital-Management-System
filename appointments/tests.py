from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, time, timedelta
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor, Department
from appointments.models import Appointment


class AppointmentWorkflowTests(TestCase):
    def setUp(self):
        # Patient
        self.patient_user = User.objects.create_user(
            username='patient_test', password='password123', role=User.ROLE_PATIENT
        )
        self.patient = Patient.objects.create(user=self.patient_user, gender='Male')

        # Another Patient
        self.patient_user2 = User.objects.create_user(
            username='patient_test2', password='password123', role=User.ROLE_PATIENT
        )
        self.patient2 = Patient.objects.create(user=self.patient_user2, gender='Female')

        # Doctor
        self.doctor_user = User.objects.create_user(
            username='doctor_test', password='password123', role=User.ROLE_DOCTOR
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            qualification='MD'
        )

        self.tomorrow = date.today() + timedelta(days=1)
        self.slot_time = time(10, 0)

    def test_book_appointment_success(self):
        self.client.login(username='patient_test', password='password123')
        response = self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': self.tomorrow.isoformat(),
            'appointment_time': '10:00:00',
            'reason': 'Chest heaviness and fatigue'
        })
        self.assertEqual(response.status_code, 302)
        appt = Appointment.objects.get(patient=self.patient, doctor=self.doctor)
        self.assertEqual(appt.status, Appointment.STATUS_PENDING)
        self.assertEqual(appt.reason, 'Chest heaviness and fatigue')

    def test_prevent_booking_in_the_past(self):
        yesterday = date.today() - timedelta(days=1)
        appt = Appointment(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=yesterday,
            appointment_time=self.slot_time,
            reason='Past check'
        )
        with self.assertRaises(ValidationError):
            appt.clean()

    def test_prevent_duplicate_booking_for_same_slot(self):
        # Create first active appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.tomorrow,
            appointment_time=self.slot_time,
            status=Appointment.STATUS_CONFIRMED,
            reason='Routine visit'
        )

        # Second patient tries booking same doctor at same date and time
        self.client.login(username='patient_test2', password='password123')
        response = self.client.post(reverse('appointments:book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': self.tomorrow.isoformat(),
            'appointment_time': '10:00:00',
            'reason': 'Second booking attempt'
        })
        # Form should fail validation and not redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This time slot is already booked")
