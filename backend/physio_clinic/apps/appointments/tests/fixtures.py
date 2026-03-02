"""
Shared fixtures for appointment tests.
Import AppointmentFixtures as a mixin in TestCase subclasses.
"""
from datetime import time, timedelta
from django.utils import timezone
from physio_clinic.apps.accounts.models import User, DoctorProfile, PatientProfile, DoctorSchedule, UserRole
from physio_clinic.apps.services.models import Service, ServiceCategory


class AppointmentFixtures:
    """Mixin providing helper methods for test setup."""

    def make_patient(self, email='patient@test.com', password='TestPass@123'):
        user = User.objects.create_user(
            email=email, password=password,
            first_name='Test', last_name='Patient',
            role=UserRole.PATIENT, gdpr_consent=True
        )
        profile = PatientProfile.objects.create(user=user)
        return user, profile

    def make_doctor(self, email='doctor@test.com', days=range(5)):
        """Create doctor with Mon-Fri 09:00-17:00 schedule by default."""
        user = User.objects.create_user(
            email=email, password='TestPass@123',
            first_name='Test', last_name='Doctor', role=UserRole.DOCTOR
        )
        doctor = DoctorProfile.objects.create(
            user=user, license_number=f'LIC-{email[:8]}',
            consultation_fee=150
        )
        for day in days:
            DoctorSchedule.objects.create(
                doctor=doctor, day_of_week=day,
                start_time=time(9, 0), end_time=time(17, 0), is_available=True
            )
        return user, doctor

    def make_service(self, name='Test Service'):
        cat, _ = ServiceCategory.objects.get_or_create(name='General')
        from django.utils.text import slugify
        svc, _ = Service.objects.get_or_create(
            name=name,
            defaults={
                'slug': slugify(name),
                'short_description': 'Test service',
                'description': 'A test physiotherapy service',
                'session_duration_minutes': 60,
                'price_per_session': 150,
                'is_active': True,
                'category': cat,
            }
        )
        return svc

    def next_weekday(self, days_ahead=1):
        """Return the next weekday date at least `days_ahead` days in the future."""
        d = timezone.now().date() + timedelta(days=days_ahead)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        return d
