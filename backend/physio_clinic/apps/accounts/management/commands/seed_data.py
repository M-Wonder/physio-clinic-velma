"""
Management command to seed demo data for local development ONLY.
Refuses to run when DEBUG=False so it can never seed a real deployment.
"""
import os
import secrets
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# Services are loaded by migration services.0002_neuromotion_services, so they
# already exist after `migrate`. This command only adds DEMO people for local
# development — clearly fake accounts, never real staff.
DOCTORS = [
    {'email': 'therapist.demo1@example.com', 'first_name': 'Demo', 'last_name': 'Therapist One',
     'license': 'DEMO-001', 'bio': 'Demo account for local development.', 'years_experience': 5,
     'specialties': ['musculoskeletal-physiotherapy', 'hands-on-soft-tissue-therapy'],
     'schedule': {0: ('09:00', '17:00'), 1: ('09:00', '17:00'), 2: ('09:00', '17:00'), 3: ('09:00', '17:00'), 4: ('09:00', '17:00')}},
    {'email': 'therapist.demo2@example.com', 'first_name': 'Demo', 'last_name': 'Therapist Two',
     'license': 'DEMO-002', 'bio': 'Demo account for local development.', 'years_experience': 8,
     'specialties': ['neurological-rehabilitation', 'home-physiotherapy'],
     'schedule': {1: ('09:00', '17:00'), 2: ('09:00', '17:00'), 3: ('09:00', '17:00'), 4: ('09:00', '17:00'), 5: ('09:00', '13:00')}},
]


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
        self._create_doctors(password)
        self._create_sample_patient(password)
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(f'\nAll demo accounts share this password: {password}')
        self.stdout.write('(Set $SEED_DEMO_PASSWORD or pass --password to make this repeatable.)')

    def _create_doctors(self, password):
        from django.contrib.auth import get_user_model
        from physio_clinic.apps.accounts.models import DoctorProfile, DoctorSchedule, UserRole
        from physio_clinic.apps.services.models import Service
        from datetime import time
        User = get_user_model()

        for d in DOCTORS:
            user, created = User.objects.get_or_create(
                email=d['email'],
                defaults={
                    'first_name': d['first_name'], 'last_name': d['last_name'],
                    'role': UserRole.DOCTOR, 'is_active': True,
                }
            )
            user.set_password(password)
            user.is_active = True
            user.role = UserRole.DOCTOR
            user.first_name = d['first_name']
            user.last_name = d['last_name']
            user.save()

            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': d['license'], 'bio': d['bio'],
                    'years_experience': d['years_experience'],
                    'consultation_fee': 150, 'is_accepting_patients': True,
                }
            )

            for sname in d['specialties']:
                try:
                    svc = Service.objects.get(slug=sname)
                    profile.specialties.add(svc)
                except Service.DoesNotExist:
                    self.stdout.write(f'    Warning: service "{sname}" not found')

            for day, (start, end) in d['schedule'].items():
                DoctorSchedule.objects.get_or_create(
                    doctor=profile, day_of_week=day,
                    defaults={
                        'start_time': time.fromisoformat(start),
                        'end_time': time.fromisoformat(end),
                        'is_available': True, 'max_patients': 8,
                    }
                )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  ✓ {status} {d["first_name"]} {d["last_name"]}')

    def _create_sample_patient(self, password):
        from django.contrib.auth import get_user_model
        from physio_clinic.apps.accounts.models import PatientProfile, UserRole
        User = get_user_model()

        user, created = User.objects.get_or_create(
            email='patient@example.com',
            defaults={
                'first_name': 'Alex', 'last_name': 'Patient',
                'role': UserRole.PATIENT, 'is_active': True,
                'gdpr_consent': True,
            }
        )
        user.set_password(password)
        user.is_active = True
        user.gdpr_consent = True
        user.save()

        PatientProfile.objects.get_or_create(
            user=user,
            defaults={'blood_type': 'O+'}
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(f'  ✓ {status} patient: patient@example.com')
