from django.test import TestCase
from django.urls import reverse
from datetime import date, time, timedelta
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from records.models import MedicalRecord, Prescription, PrescriptionMedicine


class RecordsAndPrescriptionsTests(TestCase):
    def setUp(self):
        # Doctor
        self.doc_user = User.objects.create_user(
            username='dr_test', password='password123', role=User.ROLE_DOCTOR
        )
        self.doctor = Doctor.objects.create(
            user=self.doc_user, specialization='Neurology', qualification='MD'
        )

        # Another Doctor
        self.other_doc_user = User.objects.create_user(
            username='other_doc', password='password123', role=User.ROLE_DOCTOR
        )
        self.other_doc = Doctor.objects.create(
            user=self.other_doc_user, specialization='Dermatology', qualification='MD'
        )

        # Patient 1
        self.pat_user1 = User.objects.create_user(
            username='patient_one', password='password123', role=User.ROLE_PATIENT
        )
        self.patient1 = Patient.objects.create(user=self.pat_user1, gender='Male')

        # Patient 2
        self.pat_user2 = User.objects.create_user(
            username='patient_two', password='password123', role=User.ROLE_PATIENT
        )
        self.patient2 = Patient.objects.create(user=self.pat_user2, gender='Female')

        # Appointment for Patient 1 with Doctor
        self.appt = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(11, 0),
            status=Appointment.STATUS_CONFIRMED,
            reason='Frequent headaches'
        )

    def test_consultation_creates_record_and_prescription(self):
        self.client.login(username='dr_test', password='password123')

        post_data = {
            'diagnosis': 'Migraine with Aura',
            'symptoms': 'Unilateral throbbing headache, photophobia',
            'treatment': 'Triptans for acute episodes; lifestyle modification',
            'notes': 'Keep headache diary',
            'follow_up_date': (date.today() + timedelta(days=14)).isoformat(),
            'notes_rx': 'Take medication at onset of headache',

            # Management form for medicines formset
            'medicines-TOTAL_FORMS': '1',
            'medicines-INITIAL_FORMS': '0',
            'medicines-MIN_NUM_FORMS': '0',
            'medicines-MAX_NUM_FORMS': '1000',
            'medicines-0-medicine_name': 'Sumatriptan Succinate',
            'medicines-0-dosage': '50 mg',
            'medicines-0-frequency': 'As needed',
            'medicines-0-duration': '6 doses',
            'medicines-0-instructions': 'Take at migraine onset',
        }

        response = self.client.post(
            reverse('records:create_consultation_record', args=[self.appt.id]),
            data=post_data
        )
        self.assertEqual(response.status_code, 302)

        # Appointment is now completed
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, Appointment.STATUS_COMPLETED)

        # Medical Record created
        rec = MedicalRecord.objects.get(appointment=self.appt)
        self.assertEqual(rec.diagnosis, 'Migraine with Aura')
        self.assertTrue(rec.has_prescription)

        # Prescription and Medicine created
        rx = rec.prescription
        self.assertEqual(rx.medicines.count(), 1)
        self.assertEqual(rx.medicines.first().medicine_name, 'Sumatriptan Succinate')

    def test_medical_record_privacy_restriction(self):
        # Create record
        rec = MedicalRecord.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.appt,
            diagnosis='Private Condition',
            symptoms='Confidential Symptoms',
            treatment='Therapy'
        )

        # Patient 1 can view own record
        self.client.login(username='patient_one', password='password123')
        resp = self.client.get(reverse('records:medical_record_detail', args=[rec.id]))
        self.assertEqual(resp.status_code, 200)
        self.client.logout()

        # Patient 2 CANNOT view Patient 1's record (should redirect)
        self.client.login(username='patient_two', password='password123')
        resp = self.client.get(reverse('records:medical_record_detail', args=[rec.id]))
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
