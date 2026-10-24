"""
Load the Neuromotion Physiotherapy Clinic service catalogue.

Runs once per database (on every deploy that has not yet applied it), so a
fresh Render/Docker database comes up with the clinic's six services already
in place — no manual seeding step. After this runs, edit services freely in
Django admin; later deploys will not overwrite those edits.

The previous generic demo services are hidden (is_active=False), not deleted,
so any appointments that reference them keep their history.
"""
from django.db import migrations
from django.utils.text import slugify

# conditions_treated is stored comma-separated (see the field's help_text);
# none of the items below contain a comma themselves.
SERVICES = [
    {
        'name': 'Musculoskeletal Physiotherapy', 'icon': '🦴',
        'short_description': 'Care for back and neck pain, joint problems, sports injuries and posture.',
        'description': 'Assessment and treatment for pain and movement problems in the muscles, joints and spine, '
                       'with a personalised plan to help you move better and prevent recurrence.',
        'conditions_treated': 'Back & neck pain, Joint pain and stiffness, Sports & activity-related injuries, '
                              'Postural problems, Arthritis management',
    },
    {
        'name': 'Neurological Rehabilitation', 'icon': '🧠',
        'short_description': 'Rehabilitation to improve movement, balance and coordination.',
        'description': 'Rehabilitation for people whose movement has been affected by a neurological condition, '
                       'focused on mobility, balance and function in daily life.',
        'conditions_treated': 'Stroke rehabilitation, Weakness and mobility problems, Balance and coordination, '
                              'Neurological movement disorders',
    },
    {
        'name': "Women's Health Physiotherapy", 'icon': '🤰',
        'short_description': 'Physiotherapy for pregnancy, postnatal recovery and pelvic health.',
        'description': 'Support for women before and after childbirth and for pelvic health concerns, '
                       'with gentle, evidence-informed rehabilitation.',
        'conditions_treated': 'Prenatal & postnatal rehabilitation, Diastasis recti rehabilitation, Pelvic health, '
                              'Recovery after childbirth',
    },
    {
        'name': 'Rehabilitation & Recovery', 'icon': '🏃',
        'short_description': 'Structured rehabilitation to rebuild strength and mobility.',
        'description': 'Progressive rehabilitation after surgery or injury, rebuilding strength, mobility and '
                       'the ability to do the things that matter to you.',
        'conditions_treated': 'Post-operative rehabilitation, Strength & conditioning, Mobility restoration, '
                              'Functional rehabilitation',
    },
    {
        'name': 'Hands-On & Soft Tissue Therapy', 'icon': '🙌',
        'short_description': 'Manual techniques to ease muscle tension and pain.',
        'description': 'Hands-on treatment to reduce pain and muscle tension and improve movement, '
                       'often combined with an exercise programme.',
        'conditions_treated': 'Deep tissue techniques, Trigger point release, Manual therapy, '
                              'Muscle and soft-tissue management',
    },
    {
        'name': 'Home Physiotherapy', 'icon': '🏠',
        'short_description': 'Individualised physiotherapy in the comfort of your home.',
        'description': 'Physiotherapy delivered at home, including functional assessments, rehabilitation and '
                       'mobility support, with guidance for caregivers.',
        'conditions_treated': 'Individualised treatment in the comfort of your home, Functional assessments, '
                              'Rehabilitation and mobility support, Caregiver guidance',
    },
]

# Generic demo services from the original seed data — hidden, never deleted.
OLD_DEMO_NAMES = [
    'Musculoskeletal Rehabilitation', 'Sports Injury Management', 'Post-Surgical Rehabilitation',
    'Cardiopulmonary Physiotherapy', 'Pain Management', 'Geriatric Physiotherapy',
]


def load_services(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    ServiceCategory = apps.get_model('services', 'ServiceCategory')

    category, _ = ServiceCategory.objects.get_or_create(name='Physiotherapy', defaults={'icon': '🏃'})

    for order, data in enumerate(SERVICES, start=1):
        Service.objects.update_or_create(
            slug=slugify(data['name']),
            defaults={**data, 'category': category, 'order': order,
                      'session_duration_minutes': 60, 'is_active': True},
        )
    Service.objects.filter(name__in=OLD_DEMO_NAMES).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [('services', '0001_initial')]

    operations = [migrations.RunPython(load_services, migrations.RunPython.noop)]
