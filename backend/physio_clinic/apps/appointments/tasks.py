"""
Celery tasks for appointment reminders and cleanup.
"""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('physio_clinic')


@shared_task(name='appointments.send_reminders', bind=True, max_retries=3)
def send_appointment_reminders(self):
    """Send 24h reminder for appointments scheduled for tomorrow."""
    from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus
    from physio_clinic.apps.notifications.tasks import send_appointment_reminder

    tomorrow = timezone.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status__in=(AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED),
        reminder_sent=False,
    ).select_related('patient__user', 'doctor__user')

    count = 0
    for appointment in appointments:
        send_appointment_reminder.delay(str(appointment.id))
        count += 1

    logger.info('Queued %d appointment reminders for %s', count, tomorrow)
    return f'Queued {count} reminders'


@shared_task(name='appointments.cleanup_cache')
def cleanup_slot_cache():
    """Remove stale slot cache entries for past dates."""
    from django.core.cache import cache
    # Cache keys expire automatically with TTL, but we log for monitoring
    logger.info('Slot cache cleanup task ran')
