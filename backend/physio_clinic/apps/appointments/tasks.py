import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('physio_clinic')


@shared_task
def send_appointment_reminders():
    """Hourly: queue reminders for appointments starting within the next 24h."""
    from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus
    from physio_clinic.apps.notifications.tasks import send_appointment_reminder

    now = timezone.localtime()
    today = now.date()
    rows = Appointment.objects.filter(
        appointment_date__in=[today, today + timedelta(days=1)],
        status__in=(AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED),
        reminder_sent=False,
    ).values_list('id', 'appointment_date', 'start_time')

    queued = 0
    for pk, day, start in rows:
        starts_at = timezone.make_aware(datetime.combine(day, start))
        if timedelta(0) < starts_at - now <= timedelta(hours=24):
            send_appointment_reminder.delay(str(pk))
            queued += 1
    logger.info('Queued %d appointment reminders', queued)
    return queued
