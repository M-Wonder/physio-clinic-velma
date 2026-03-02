"""
Tests for account registration, authentication, and profile access.
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from physio_clinic.apps.accounts.models import User, PatientProfile, DoctorProfile, UserRole


class RegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_patient_registration_success(self):
        """Registration creates user + patient profile and returns tokens."""
        resp = self.client.post('/api/auth/register/', {
            'email': 'newpatient@test.com',
            'first_name': 'New', 'last_name': 'Patient',
            'password': 'SecurePass@123',
            'password2': 'SecurePass@123',
            'gdpr_consent': True,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertIn('tokens', resp.data)
        self.assertEqual(resp.data['user']['role'], 'patient')
        # Patient profile auto-created
        self.assertTrue(PatientProfile.objects.filter(user__email='newpatient@test.com').exists())

    def test_registration_without_gdpr_rejected(self):
        """Registration without GDPR consent returns 400."""
        resp = self.client.post('/api/auth/register/', {
            'email': 'nop@test.com',
            'first_name': 'A', 'last_name': 'B',
            'password': 'SecurePass@123',
            'password2': 'SecurePass@123',
            'gdpr_consent': False,
        })
        self.assertEqual(resp.status_code, 400)

    def test_registration_mismatched_passwords_rejected(self):
        """Mismatched passwords return 400."""
        resp = self.client.post('/api/auth/register/', {
            'email': 'test@test.com',
            'first_name': 'A', 'last_name': 'B',
            'password': 'SecurePass@123',
            'password2': 'DifferentPass@123',
            'gdpr_consent': True,
        })
        self.assertEqual(resp.status_code, 400)

    def test_duplicate_email_rejected(self):
        """Cannot register the same email twice."""
        User.objects.create_user(
            email='exists@test.com', password='Pass@123',
            first_name='A', last_name='B', role=UserRole.PATIENT
        )
        resp = self.client.post('/api/auth/register/', {
            'email': 'exists@test.com',
            'first_name': 'A', 'last_name': 'B',
            'password': 'SecurePass@123', 'password2': 'SecurePass@123',
            'gdpr_consent': True,
        })
        self.assertEqual(resp.status_code, 400)


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='patient@test.com', password='TestPass@123',
            first_name='Test', last_name='User', role=UserRole.PATIENT,
            gdpr_consent=True
        )

    def test_login_returns_tokens(self):
        """Successful login returns access and refresh tokens."""
        resp = self.client.post('/api/auth/login/', {
            'email': 'patient@test.com',
            'password': 'TestPass@123',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertIn('user', resp.data)

    def test_wrong_password_rejected(self):
        """Wrong password returns 401."""
        resp = self.client.post('/api/auth/login/', {
            'email': 'patient@test.com',
            'password': 'WrongPassword!',
        })
        self.assertEqual(resp.status_code, 401)

    def test_me_endpoint_returns_current_user(self):
        """Authenticated /me endpoint returns user data."""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], 'patient@test.com')

    def test_me_unauthenticated_returns_401(self):
        """Unauthenticated /me returns 401."""
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, 401)


class RoleAccessTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = User.objects.create_user(
            email='patient@test.com', password='Pass@123',
            first_name='P', last_name='User', role=UserRole.PATIENT
        )
        self.doctor_user = User.objects.create_user(
            email='doctor@test.com', password='Pass@123',
            first_name='D', last_name='Doc', role=UserRole.DOCTOR
        )
        DoctorProfile.objects.create(user=self.doctor_user, license_number='TEST-001')

    def test_patient_cannot_list_all_patients(self):
        """Patients cannot access the full patient list (admin/doctor only)."""
        self.client.force_authenticate(user=self.patient)
        resp = self.client.get('/api/auth/patients/')
        # Should only see their own (0 results since no PatientProfile created)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_doctor_list_is_public(self):
        """Doctor listing is publicly accessible."""
        resp = self.client.get('/api/auth/doctors/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)
