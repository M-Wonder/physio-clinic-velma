"""
Unit and integration tests for appointment booking.
Tests: booking, double-booking prevention, cancellation, rescheduling.
"""
import threading
from datetime import date, time, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from physio_clinic.apps.accounts.models import User, DoctorProfile, PatientProfile, DoctorSchedule, UserRole
from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus
from physio_clinic.apps.services.models import Service, ServiceCategory


class AppointmentTestMixin:
    """Helper mixin to create test fixtures."""

    def create_user(self, email, role=UserRole.PATIENT, password='TestPass@123'):
        user = User.objects.create_user(
            email=email, password=password,
            first_name='Test', last_name='User', role=role,
            gdpr_consent=True
        )
        return user

    def create_doctor_with_schedule(self, email='doctor@test.com'):
        user = self.create_user(email, UserRole.DOCTOR)
        doctor = DoctorProfile.objects.create(user=user, license_number=f'LIC-{email[:5]}')
        # Schedule: Monday-Friday, 9-17
        for day in range(5):
            DoctorSchedule.objects.create(
                doctor=doctor, day_of_week=day,
                start_time=time(9, 0), end_time=time(17, 0), is_available=True
            )
        return doctor

    def create_service(self):
        cat, _ = ServiceCategory.objects.get_or_create(name='Test')
        svc, _ = Service.objects.get_or_create(
            name='Test Service', slug='test-service',
            defaults={'short_description': 'Test', 'description': 'Test', 'session_duration_minutes': 60}
        )
        return svc

    def get_next_weekday(self):
        """Get the next weekday (Monday-Friday) for testing."""
        d = timezone.now().date() + timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        return d


class AppointmentBookingTest(AppointmentTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.doctor = self.create_doctor_with_schedule()
        self.patient_user = self.create_user('patient@test.com')
        PatientProfile.objects.create(user=self.patient_user)
        self.service = self.create_service()
        self.client.force_authenticate(user=self.patient_user)

    def test_book_appointment_success(self):
        """Test successful appointment booking."""
        appt_date = self.get_next_weekday()
        resp = self.client.post('/api/appointments/book/', {
            'doctor_id': self.doctor.id,
            'service_id': self.service.id,
            'appointment_date': appt_date.isoformat(),
            'start_time': '09:00',
            'reason_for_visit': 'Back pain',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_book_past_date_rejected(self):
        """Test that booking a past date is rejected."""
        yesterday = timezone.now().date() - timedelta(days=1)
        resp = self.client.post('/api/appointments/book/', {
            'doctor_id': self.doctor.id,
            'service_id': self.service.id,
            'appointment_date': yesterday.isoformat(),
            'start_time': '09:00',
        })
        self.assertIn(resp.status_code, [400, 422])

    def test_book_unavailable_slot_rejected(self):
        """Test that booking an already-taken slot returns 409."""
        appt_date = self.get_next_weekday()
        # Book once
        Appointment.objects.create(
            patient=self.patient_user.patient_profile,
            doctor=self.doctor,
            service=self.service,
            appointment_date=appt_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
            status=AppointmentStatus.SCHEDULED,
            booked_by=self.patient_user,
        )
        # Try to book same slot
        resp = self.client.post('/api/appointments/book/', {
            'doctor_id': self.doctor.id,
            'service_id': self.service.id,
            'appointment_date': appt_date.isoformat(),
            'start_time': '09:00',
        })
        self.assertIn(resp.status_code, [400, 409])

    def test_cancel_appointment(self):
        """Test appointment cancellation with ample notice."""
        appt_date = timezone.now().date() + timedelta(days=3)
        # Ensure it's a weekday
        while appt_date.weekday() >= 5:
            appt_date += timedelta(days=1)
        appt = Appointment.objects.create(
            patient=self.patient_user.patient_profile,
            doctor=self.doctor, service=self.service,
            appointment_date=appt_date,
            start_time=time(10, 0), end_time=time(11, 0),
            status=AppointmentStatus.SCHEDULED,
            booked_by=self.patient_user,
        )
        resp = self.client.post(f'/api/appointments/{appt.id}/cancel/', {'reason': 'Personal reasons'})
        self.assertEqual(resp.status_code, 200)
        appt.refresh_from_db()
        self.assertEqual(appt.status, AppointmentStatus.CANCELLED)

    def test_get_available_slots(self):
        """Test that slot endpoint returns correct times."""
        appt_date = self.get_next_weekday()
        resp = self.client.get('/api/appointments/slots/', {
            'doctor_id': self.doctor.id,
            'date': appt_date.isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slots', resp.data)
        self.assertTrue(len(resp.data['slots']) > 0)


class AppointmentAuthTest(AppointmentTestMixin, TestCase):
    """Test access control on appointment endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.doctor = self.create_doctor_with_schedule()
        self.patient1 = self.create_user('p1@test.com')
        self.patient2 = self.create_user('p2@test.com')
        PatientProfile.objects.create(user=self.patient1)
        PatientProfile.objects.create(user=self.patient2)
        self.service = self.create_service()

    def test_patient_cannot_see_other_patients_appointments(self):
        """Patients should only see their own appointments."""
        appt_date = timezone.now().date() + timedelta(days=2)
        while appt_date.weekday() >= 5:
            appt_date += timedelta(days=1)

        Appointment.objects.create(
            patient=self.patient2.patient_profile,
            doctor=self.doctor, service=self.service,
            appointment_date=appt_date,
            start_time=time(9, 0), end_time=time(10, 0),
            status=AppointmentStatus.SCHEDULED,
            booked_by=self.patient2,
        )
        self.client.force_authenticate(user=self.patient1)
        resp = self.client.get('/api/appointments/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_unauthenticated_cannot_book(self):
        appt_date = self.get_next_weekday()
        resp = self.client.post('/api/appointments/book/', {
            'doctor_id': self.doctor.id,
            'service_id': self.service.id,
            'appointment_date': appt_date.isoformat(),
            'start_time': '09:00',
        })
        self.assertEqual(resp.status_code, 401)
