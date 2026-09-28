"""
Celery tasks for notifications (email + SMS).

Flow: business event -> send_appointment_<event> -> one NotificationLog row per
enabled channel (status=pending) -> deliver_notification(log_id) sends it with
retries. Channels are retried independently.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import OperationalError
from django.utils import timezone

from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus
from physio_clinic.apps.notifications.models import NotificationLog

logger = logging.getLogger('physio_clinic')

MAX_DELIVERY_RETRIES = 5


class PermanentDeliveryError(Exception):
    """Retrying will not help (provider not configured, etc.)."""


# (email subject, email body, sms body)
TEMPLATES = {
    'confirmation': (
        'Appointment confirmed - {clinic}',
        'Hello {patient},\n\nYour {service} appointment with {doctor} is booked for '
        '{date} at {time}.\n\nIf you need to change it, please do so at least '
        '{notice_hours} hours beforehand.\n\n{clinic}\n{phone}',
        '{clinic}: appointment confirmed with {doctor} on {date} at {time}.',
    ),
    'reminder': (
        'Reminder: appointment on {date} - {clinic}',
        'Hello {patient},\n\nThis is a reminder of your {service} appointment with '
        '{doctor} on {date} at {time}.\n\n{clinic}\n{phone}',
        '{clinic} reminder: appointment with {doctor} on {date} at {time}.',
    ),
    'cancellation': (
        'Appointment cancelled - {clinic}',
        'Hello {patient},\n\nYour appointment with {doctor} on {date} at {time} has '
        'been cancelled. Please contact us or book online for a new time.\n\n{clinic}\n{phone}',
        '{clinic}: your appointment on {date} at {time} was cancelled.',
    ),
}


def _context(appt):
    return {
        'clinic': getattr(settings, 'CLINIC_NAME', 'PhysioClinic'),
        'phone': getattr(settings, 'CLINIC_PHONE', ''),
        'notice_hours': getattr(settings, 'CANCELLATION_NOTICE_HOURS', 24),
        'patient': appt.patient.user.first_name,
        'doctor': f'Dr. {appt.doctor.user.get_full_name()}',
        'service': appt.service.name if appt.service else 'physiotherapy',
        'date': appt.appointment_date.strftime('%A %d %B %Y'),
        'time': appt.start_time.strftime('%H:%M'),
    }


def _queue_notifications(appointment_id, event):
    appt = (Appointment.objects
            .select_related('patient__user', 'doctor__user', 'service')
            .filter(pk=appointment_id).first())
    if appt is None:
        logger.warning('Notification %s skipped: appointment %s not found', event, appointment_id)
        return 'appointment-not-found'

    user = appt.patient.user
    subject_t, email_t, sms_t = TEMPLATES[event]
    ctx = _context(appt)

    logs = []
    if user.email_notifications and user.email:
        logs.append(NotificationLog.objects.create(
            user=user, notification_type='email', event=event,
            subject=subject_t.format(**ctx), body=email_t.format(**ctx)))
    if user.sms_notifications and user.phone_number:
        logs.append(NotificationLog.objects.create(
            user=user, notification_type='sms', event=event, body=sms_t.format(**ctx)))

    for log in logs:
        deliver_notification.delay(log.id)
    return f'{event}: queued {len(logs)} notification(s)'


def _send_email(log):
    send_mail(log.subject, log.body, settings.DEFAULT_FROM_EMAIL,
              [log.user.email], fail_silently=False)


def _send_sms(log):
    sid, token, sender = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN,
                          settings.TWILIO_PHONE_NUMBER)
    if not (sid and token and sender):
        raise PermanentDeliveryError('Twilio is not configured')
    from twilio.rest import Client  # lazy: only needed when SMS is enabled
    Client(sid, token).messages.create(body=log.body, from_=sender, to=log.user.phone_number)


@shared_task(bind=True, acks_late=True, max_retries=MAX_DELIVERY_RETRIES)
def deliver_notification(self, log_id):
    """Send one NotificationLog row. Idempotent: already-sent rows are skipped."""
    try:
        log = NotificationLog.objects.select_related('user').get(pk=log_id)
    except NotificationLog.DoesNotExist:
        return 'missing'
    if log.status == 'sent':
        return 'already-sent'

    try:
        if log.notification_type == 'email':
            _send_email(log)
        elif log.notification_type == 'sms':
            _send_sms(log)
        else:
            raise PermanentDeliveryError(f'Unsupported type {log.notification_type}')
    except PermanentDeliveryError as exc:
        log.status, log.error_message = 'failed', str(exc)[:1000]
        log.save(update_fields=['status', 'error_message'])
        logger.error('Notification %s failed permanently: %s', log_id, exc)
        return 'failed'
    except Exception as exc:
        log.error_message = str(exc)[:1000]
        if self.request.retries >= self.max_retries:
            log.status = 'failed'
            log.save(update_fields=['status', 'error_message'])
            logger.error('Notification %s failed after retries: %s', log_id, exc)
            return 'failed'
        log.save(update_fields=['error_message'])
        raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

    log.status, log.sent_at, log.error_message = 'sent', timezone.now(), ''
    log.save(update_fields=['status', 'sent_at', 'error_message'])
    return 'sent'


_retry_db = dict(autoretry_for=(OperationalError,), retry_backoff=True, max_retries=3)


@shared_task(**_retry_db)
def send_appointment_confirmation(appointment_id):
    return _queue_notifications(appointment_id, 'confirmation')


@shared_task(**_retry_db)
def send_appointment_cancellation(appointment_id):
    return _queue_notifications(appointment_id, 'cancellation')


@shared_task(**_retry_db)
def send_appointment_reminder(appointment_id):
    # Claim atomically so concurrent runs can never send two reminders.
    claimed = Appointment.objects.filter(
        pk=appointment_id, reminder_sent=False,
        status__in=(AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED),
    ).update(reminder_sent=True, reminder_sent_at=timezone.now())
    if not claimed:
        return 'skipped'
    return _queue_notifications(appointment_id, 'reminder')