# backend/physio_clinic/apps/accounts/management/commands/seed_data.py
"""
Management command to seed demo data for local development ONLY.
Refuses to run when DEBUG=False so it can never seed a real deployment.
"""
import os
import secrets
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

SERVICES = [ ... ]   # unchanged
DOCTORS = [ ... ]    # unchanged


class Command(BaseCommand):
    help = 'Seed demo data for local development. Refuses to run with DEBUG=False.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default=os.environ.get('SEED_DEMO_PASSWORD'),
            help='Password for all seeded demo accounts. Defaults to $SEED_DEMO_PASSWORD, '
                 'or a random one-time password if neither is set.',
        )

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError(
                'Refusing to seed demo data: DEBUG=False. '
                'This command is for local development only.'
            )

        password = kwargs['password'] or secrets.token_urlsafe(12)
        self.stdout.write('Seeding demo data...')
        self._create_services()
        self._create_doctors(password)
        self._create_sample_patient(password)
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(f'\nAll demo accounts share this password: {password}')
        self.stdout.write('(Set $SEED_DEMO_PASSWORD or pass --password to make this repeatable.)')

    def _create_services(self):
        ...  # unchanged

    def _create_doctors(self, password):
        from django.contrib.auth import get_user_model
        from physio_clinic.apps.accounts.models import DoctorProfile, DoctorSchedule, UserRole
        from physio_clinic.apps.services.models import Service
        from datetime import time
        User = get_user_model()

        for d in DOCTORS:
            user, created = User.objects.get_or_create(
                email=d['email'],
                defaults={'first_name': d['first_name'], 'last_name': d['last_name'],
                          'role': UserRole.DOCTOR, 'is_active': True},
            )
            user.set_password(password)
            user.is_active = True
            user.role = UserRole.DOCTOR
            user.first_name, user.last_name = d['first_name'], d['last_name']
            user.save()
            # ... rest unchanged (profile, specialties, schedule)

    def _create_sample_patient(self, password):
        from django.contrib.auth import get_user_model
        from physio_clinic.apps.accounts.models import PatientProfile, UserRole
        User = get_user_model()

        user, created = User.objects.get_or_create(
            email='patient@example.com',
            defaults={'first_name': 'Alex', 'last_name': 'Patient',
                      'role': UserRole.PATIENT, 'is_active': True, 'gdpr_consent': True},
        )
        user.set_password(password)
        user.is_active = True
        user.gdpr_consent = True
        user.save()
        PatientProfile.objects.get_or_create(user=user, defaults={'blood_type': 'O+'})