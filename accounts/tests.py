from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor, Department


class AccountsAndRoleTests(TestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(
            username='testpatient',
            email='testpatient@example.com',
            password='testpassword123',
            role=User.ROLE_PATIENT
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            gender='Male'
        )

        self.doctor_user = User.objects.create_user(
            username='testdoctor',
            email='testdoctor@example.com',
            password='testpassword123',
            role=User.ROLE_DOCTOR
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization='General Practitioner',
            qualification='MBBS'
        )

        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@example.com',
            password='testpassword123',
            role=User.ROLE_ADMIN
        )

    def test_patient_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newpatient',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'newpatient@example.com',
            'phone': '1234567890',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'gender': 'Female',
            'blood_group': 'O+',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newpatient')
        self.assertEqual(new_user.role, User.ROLE_PATIENT)
        self.assertTrue(hasattr(new_user, 'patient_profile'))
        self.assertEqual(new_user.patient_profile.blood_group, 'O+')

    def test_role_based_redirection(self):
        # Patient login -> patient dashboard
        self.client.login(username='testpatient', password='testpassword123')
        resp = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(resp, reverse('patients:patient_dashboard'))
        self.client.logout()

        # Doctor login -> doctor dashboard
        self.client.login(username='testdoctor', password='testpassword123')
        resp = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(resp, reverse('doctors:doctor_dashboard'))
        self.client.logout()

        # Admin login -> admin dashboard
        self.client.login(username='testadmin', password='testpassword123')
        resp = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(resp, reverse('dashboard:admin_dashboard'))
        self.client.logout()

    def test_permission_enforcement(self):
        # Patient trying to access doctor portal should be redirected
        self.client.login(username='testpatient', password='testpassword123')
        resp = self.client.get(reverse('doctors:doctor_dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.client.logout()
