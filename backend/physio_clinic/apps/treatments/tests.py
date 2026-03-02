"""Tests for treatment records and file access control."""
from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from physio_clinic.apps.accounts.models import User, DoctorProfile, PatientProfile, UserRole
from physio_clinic.apps.treatments.models import TreatmentRecord


class TreatmentRecordAccessTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Doctor
        self.doctor_user = User.objects.create_user(
            email='doc@test.com', password='Pass@123',
            first_name='D', last_name='Doc', role=UserRole.DOCTOR
        )
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user, license_number='LIC-001')
        # Patient 1
        self.patient1_user = User.objects.create_user(
            email='p1@test.com', password='Pass@123',
            first_name='P1', last_name='Patient', role=UserRole.PATIENT
        )
        self.patient1 = PatientProfile.objects.create(user=self.patient1_user)
        # Patient 2
        self.patient2_user = User.objects.create_user(
            email='p2@test.com', password='Pass@123',
            first_name='P2', last_name='Patient', role=UserRole.PATIENT
        )
        self.patient2 = PatientProfile.objects.create(user=self.patient2_user)
        # Treatment for patient1
        self.record = TreatmentRecord.objects.create(
            patient=self.patient1, doctor=self.doctor,
            visit_date=date.today(),
            chief_complaint='Back pain',
            diagnosis='Lumbar strain',
            treatment_given='Massage and exercise',
        )

    def test_patient_can_view_own_records(self):
        self.client.force_authenticate(user=self.patient1_user)
        resp = self.client.get('/api/treatments/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_patient_cannot_view_other_patients_records(self):
        self.client.force_authenticate(user=self.patient2_user)
        resp = self.client.get('/api/treatments/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_doctor_can_view_their_patient_records(self):
        self.client.force_authenticate(user=self.doctor_user)
        resp = self.client.get('/api/treatments/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_patient_cannot_create_treatment_record(self):
        """Only doctors can create treatment records."""
        self.client.force_authenticate(user=self.patient1_user)
        resp = self.client.post('/api/treatments/', {
            'visit_date': str(date.today()),
            'chief_complaint': 'test',
            'diagnosis': 'test',
            'treatment_given': 'test',
        })
        self.assertEqual(resp.status_code, 403)
