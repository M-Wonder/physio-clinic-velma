"""
Celery application configuration for PhysioClinic.
Handles async tasks: notifications, reminders, and background jobs.
"""
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'physio_clinic.settings.base')

app = Celery('physio_clinic')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks (run via celery beat)
app.conf.beat_schedule = {
    # Send appointment reminders 24h before
    'send-appointment-reminders': {
        'task': 'physio_clinic.apps.appointments.tasks.send_appointment_reminders',
        'schedule': 3600.0,  # Every hour
    },
    # Clean up expired slots cache
    'cleanup-slot-cache': {
        'task': 'physio_clinic.apps.appointments.tasks.cleanup_slot_cache',
        'schedule': 86400.0,  # Daily
    },
}
