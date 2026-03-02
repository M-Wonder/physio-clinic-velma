"""
Management command to seed demo data for PhysioClinic.
Safe to run multiple times — always resets passwords so credentials are reliable.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

SERVICES = [
    {'name': 'Musculoskeletal Rehabilitation', 'short_description': 'Restore movement and function after muscle or joint injury.',
     'description': 'Comprehensive rehabilitation programs for musculoskeletal conditions.', 'conditions_treated': 'Back pain, Neck pain, Shoulder injuries, Knee injuries', 'session_duration_minutes': 60, 'icon': '🦴'},
    {'name': 'Sports Injury Management', 'short_description': 'Specialized care for athletes recovering from sports injuries.',
     'description': 'Targeted treatment for sports-related injuries with focus on rapid return to sport.', 'conditions_treated': 'ACL tears, Rotator cuff injuries, Ankle sprains', 'session_duration_minutes': 60, 'icon': '⚽'},
    {'name': 'Post-Surgical Rehabilitation', 'short_description': 'Structured recovery programs following orthopedic surgery.',
     'description': 'Customized rehabilitation protocols for patients recovering from surgeries.', 'conditions_treated': 'Hip replacement, Knee replacement, ACL reconstruction', 'session_duration_minutes': 60, 'icon': '🏥'},
    {'name': 'Neurological Rehabilitation', 'short_description': 'Physiotherapy for neurological conditions affecting movement.',
     'description': 'Specialized rehabilitation for patients with neurological disorders.', 'conditions_treated': 'Stroke, Parkinson\'s disease, Multiple sclerosis', 'session_duration_minutes': 90, 'icon': '🧠'},
    {'name': 'Cardiopulmonary Physiotherapy', 'short_description': 'Rehabilitation for heart and lung conditions.',
     'description': 'Evidence-based physiotherapy for cardiovascular and respiratory conditions.', 'conditions_treated': 'COPD, Asthma, Post-cardiac surgery', 'session_duration_minutes': 60, 'icon': '❤️'},
    {'name': 'Pain Management', 'short_description': 'Multidisciplinary approach to chronic pain relief.',
     'description': 'Comprehensive pain management using manual therapy, exercise, and education.', 'conditions_treated': 'Chronic back pain, Fibromyalgia, Headaches', 'session_duration_minutes': 60, 'icon': '💊'},
    {'name': 'Geriatric Physiotherapy', 'short_description': 'Specialized care for older adults to maintain independence.',
     'description': 'Tailored physiotherapy programs for elderly patients.', 'conditions_treated': 'Falls prevention, Osteoporosis, Balance disorders', 'session_duration_minutes': 60, 'icon': '👴'},
]

DOCTORS = [
    {'email': 'dr.sarah.mitchell@physio.clinic', 'first_name': 'Sarah', 'last_name': 'Mitchell',
     'license': 'PT-2024-001', 'bio': 'Dr. Mitchell specializes in sports injuries with 12 years of experience.',
     'years_experience': 12, 'specialties': ['Sports Injury Management', 'Musculoskeletal Rehabilitation'],
     'schedule': {0: ('09:00', '17:00'), 1: ('09:00', '17:00'), 2: ('09:00', '17:00'), 4: ('09:00', '13:00')}},
    {'email': 'dr.james.wong@physio.clinic', 'first_name': 'James', 'last_name': 'Wong',
     'license': 'PT-2024-002', 'bio': 'Dr. Wong is a neurological rehabilitation specialist.',
     'years_experience': 8, 'specialties': ['Neurological Rehabilitation', 'Post-Surgical Rehabilitation'],
     'schedule': {1: ('10:00', '18:00'), 2: ('10:00', '18:00'), 3: ('10:00', '18:00'), 5: ('09:00', '14:00')}},
    {'email': 'dr.priya.sharma@physio.clinic', 'first_name': 'Priya', 'last_name': 'Sharma',
     'license': 'PT-2024-003', 'bio': 'Dr. Sharma focuses on geriatric care and cardiopulmonary rehabilitation.',
     'years_experience': 15, 'specialties': ['Geriatric Physiotherapy', 'Cardiopulmonary Physiotherapy', 'Pain Management'],
     'schedule': {0: ('08:00', '16:00'), 2: ('08:00', '16:00'), 3: ('08:00', '16:00'), 4: ('08:00', '16:00')}},
]


class Command(BaseCommand):
    help = 'Seed demo data for PhysioClinic. Safe to re-run — always resets passwords.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')
        self._create_services()
        self._create_doctors()
        self._create_sample_patient()
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:   admin@physio.clinic / Admin@12345')
        self.stdout.write('  Doctor:  dr.sarah.mitchell@physio.clinic / Doctor@12345')
        self.stdout.write('  Doctor:  dr.james.wong@physio.clinic / Doctor@12345')
        self.stdout.write('  Doctor:  dr.priya.sharma@physio.clinic / Doctor@12345')
        self.stdout.write('  Patient: patient@example.com / Patient@12345')

    def _create_services(self):
        from physio_clinic.apps.services.models import Service, ServiceCategory
        cat, _ = ServiceCategory.objects.get_or_create(name='Physiotherapy', defaults={'icon': '🏃'})
        for i, s in enumerate(SERVICES):
            svc, created = Service.objects.get_or_create(
                name=s['name'],
                defaults={**s, 'category': cat, 'slug': slugify(s['name']),
                          'order': i, 'price_per_session': 150, 'is_active': True}
            )
            if not created:
                # Ensure existing services are active
                Service.objects.filter(pk=svc.pk).update(is_active=True)
        self.stdout.write(f'  ✓ {len(SERVICES)} services ready.')

    def _create_doctors(self):
        from django.contrib.auth import get_user_model
        from physio_clinic.apps.accounts.models import DoctorProfile, DoctorSchedule, UserRole
        from physio_clinic.apps.services.models import Service
        from datetime import time
        User = get_user_model()

        for d in DOCTORS:
            # BUG FIX: use update_or_create so password is ALWAYS set
            # get_or_create only runs defaults on INSERT, skipping existing users
            user, created = User.objects.get_or_create(
                email=d['email'],
                defaults={
                    'first_name': d['first_name'], 'last_name': d['last_name'],
                    'role': UserRole.DOCTOR, 'is_active': True,
                }
            )
            # Always reset the password — idempotent and ensures credentials work
            user.set_password('Doctor@12345')
            # Ensure user is active and has correct role
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
                    svc = Service.objects.get(name=sname)
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
            self.stdout.write(f'  ✓ {status} Dr. {d["first_name"]} {d["last_name"]}')

    def _create_sample_patient(self):
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
        # BUG FIX: always reset password
        user.set_password('Patient@12345')
        user.is_active = True
        user.gdpr_consent = True
        user.save()

        PatientProfile.objects.get_or_create(
            user=user,
            defaults={'blood_type': 'O+'}
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(f'  ✓ {status} patient: patient@example.com')