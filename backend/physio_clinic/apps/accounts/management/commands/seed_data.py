"""
Management command to seed demo data for PhysioClinic.
Creates sample doctors, patients, services, and appointments.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify


SERVICES = [
    {
        'name': 'Musculoskeletal Rehabilitation',
        'short_description': 'Restore movement and function after muscle or joint injury.',
        'description': 'Comprehensive rehabilitation programs for musculoskeletal conditions including sprains, strains, fractures, and joint replacements. Our therapists use evidence-based techniques to reduce pain and restore full functional capacity.',
        'conditions_treated': 'Back pain, Neck pain, Shoulder injuries, Knee injuries, Hip pain, Arthritis, Fractures',
        'session_duration_minutes': 60,
        'icon': '🦴',
    },
    {
        'name': 'Sports Injury Management',
        'short_description': 'Specialized care for athletes recovering from sports injuries.',
        'description': 'Targeted treatment for sports-related injuries with focus on rapid return to sport. Covers assessment, acute management, rehabilitation, and injury prevention strategies.',
        'conditions_treated': 'ACL tears, Rotator cuff injuries, Ankle sprains, Tennis elbow, Runner\'s knee, Hamstring strains',
        'session_duration_minutes': 60,
        'icon': '⚽',
    },
    {
        'name': 'Post-Surgical Rehabilitation',
        'short_description': 'Structured recovery programs following orthopedic surgery.',
        'description': 'Customized rehabilitation protocols for patients recovering from surgeries such as joint replacements, ligament repairs, and spinal procedures.',
        'conditions_treated': 'Hip replacement, Knee replacement, ACL reconstruction, Spinal fusion, Rotator cuff repair',
        'session_duration_minutes': 60,
        'icon': '🏥',
    },
    {
        'name': 'Neurological Rehabilitation',
        'short_description': 'Physiotherapy for neurological conditions affecting movement.',
        'description': 'Specialized rehabilitation for patients with neurological disorders. Focuses on improving motor function, balance, coordination, and independence in daily activities.',
        'conditions_treated': 'Stroke, Parkinson\'s disease, Multiple sclerosis, Spinal cord injury, Brain injury, Cerebral palsy',
        'session_duration_minutes': 90,
        'icon': '🧠',
    },
    {
        'name': 'Cardiopulmonary Physiotherapy',
        'short_description': 'Rehabilitation for heart and lung conditions.',
        'description': 'Evidence-based physiotherapy for cardiovascular and respiratory conditions, including post-cardiac surgery rehabilitation and COPD management.',
        'conditions_treated': 'COPD, Asthma, Post-cardiac surgery, Heart failure, Pulmonary fibrosis',
        'session_duration_minutes': 60,
        'icon': '❤️',
    },
    {
        'name': 'Pain Management',
        'short_description': 'Multidisciplinary approach to chronic pain relief.',
        'description': 'Comprehensive pain management using manual therapy, exercise, and education. Treats both acute and chronic pain conditions without reliance on medication.',
        'conditions_treated': 'Chronic back pain, Fibromyalgia, Complex regional pain syndrome, Headaches, Sciatica',
        'session_duration_minutes': 60,
        'icon': '💊',
    },
    {
        'name': 'Geriatric Physiotherapy',
        'short_description': 'Specialized care for older adults to maintain independence.',
        'description': 'Tailored physiotherapy programs for elderly patients focusing on fall prevention, balance training, osteoporosis management, and maintaining quality of life.',
        'conditions_treated': 'Falls prevention, Osteoporosis, Dementia-related movement issues, Age-related weakness, Balance disorders',
        'session_duration_minutes': 60,
        'icon': '👴',
    },
]

DOCTORS = [
    {
        'email': 'dr.sarah.mitchell@physio.clinic',
        'first_name': 'Sarah',
        'last_name': 'Mitchell',
        'license': 'PT-2024-001',
        'bio': 'Dr. Mitchell specializes in sports injuries and musculoskeletal rehabilitation with 12 years of experience.',
        'years_experience': 12,
        'specialties': ['Sports Injury Management', 'Musculoskeletal Rehabilitation'],
        'schedule': {0: ('09:00', '17:00'), 1: ('09:00', '17:00'), 2: ('09:00', '17:00'), 4: ('09:00', '13:00')},
    },
    {
        'email': 'dr.james.wong@physio.clinic',
        'first_name': 'James',
        'last_name': 'Wong',
        'license': 'PT-2024-002',
        'bio': 'Dr. Wong is a neurological rehabilitation specialist with extensive experience in stroke recovery.',
        'years_experience': 8,
        'specialties': ['Neurological Rehabilitation', 'Post-Surgical Rehabilitation'],
        'schedule': {1: ('10:00', '18:00'), 2: ('10:00', '18:00'), 3: ('10:00', '18:00'), 5: ('09:00', '14:00')},
    },
    {
        'email': 'dr.priya.sharma@physio.clinic',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'license': 'PT-2024-003',
        'bio': 'Dr. Sharma focuses on geriatric care and cardiopulmonary rehabilitation.',
        'years_experience': 15,
        'specialties': ['Geriatric Physiotherapy', 'Cardiopulmonary Physiotherapy', 'Pain Management'],
        'schedule': {0: ('08:00', '16:00'), 2: ('08:00', '16:00'), 3: ('08:00', '16:00'), 4: ('08:00', '16:00')},
    },
]


class Command(BaseCommand):
    help = 'Seed demo data for PhysioClinic'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')
        self._create_services()
        self._create_doctors()
        self._create_sample_patient()
        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:   admin@physio.clinic / Admin@12345')
        self.stdout.write('  Doctor:  dr.sarah.mitchell@physio.clinic / Doctor@12345')
        self.stdout.write('  Patient: patient@example.com / Patient@12345')

    def _create_services(self):
        from physio_clinic.apps.services.models import Service, ServiceCategory
        cat, _ = ServiceCategory.objects.get_or_create(name='Physiotherapy', defaults={'icon': '🏃'})
        for i, s in enumerate(SERVICES):
            Service.objects.get_or_create(
                name=s['name'],
                defaults={**s, 'category': cat, 'slug': slugify(s['name']), 'order': i, 'price_per_session': 150}
            )
        self.stdout.write(f'  Created {len(SERVICES)} services.')

    def _create_doctors(self):
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
            if created:
                user.set_password('Doctor@12345')
                user.save()

            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'license_number': d['license'], 'bio': d['bio'],
                    'years_experience': d['years_experience'], 'consultation_fee': 150,
                }
            )

            # Add specialties
            for sname in d['specialties']:
                try:
                    svc = Service.objects.get(name=sname)
                    profile.specialties.add(svc)
                except Service.DoesNotExist:
                    pass

            # Add schedule
            for day, (start, end) in d['schedule'].items():
                DoctorSchedule.objects.get_or_create(
                    doctor=profile, day_of_week=day,
                    defaults={
                        'start_time': time.fromisoformat(start),
                        'end_time': time.fromisoformat(end),
                        'is_available': True, 'max_patients': 8,
                    }
                )
        self.stdout.write(f'  Created {len(DOCTORS)} doctors.')

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
        if created:
            user.set_password('Patient@12345')
            user.save()
            PatientProfile.objects.create(user=user, blood_type='O+')
        self.stdout.write('  Created sample patient.')
