"""
Appointment Models — PhysioClinic
Handles scheduled and walk-in appointments.
"""
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class AppointmentStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'
    RESCHEDULED = 'rescheduled', 'Rescheduled'


class AppointmentType(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    WALK_IN = 'walk_in', 'Walk-in'
    EMERGENCY = 'emergency', 'Emergency'
    FOLLOW_UP = 'follow_up', 'Follow-up'
    TELECONSULT = 'teleconsult', 'Teleconsultation'


class Appointment(models.Model):
    """
    Core appointment model.
    Uses select_for_update() in booking logic to prevent double-booking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, related_name='appointments')

    appointment_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.SCHEDULED)
    appointment_type = models.CharField(max_length=20, choices=AppointmentType.choices, default=AppointmentType.SCHEDULED)

    # Notes
    reason_for_visit = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Tracking
    booked_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='booked_appointments')
    cancelled_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')
    rescheduled_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='rescheduled_to')

    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments_appointment'
        ordering = ['appointment_date', 'start_time']
        indexes = [
            models.Index(fields=['appointment_date', 'doctor', 'status']),
            models.Index(fields=['patient', 'status']),
        ]

    def __str__(self):
        return f"{self.patient.user.get_full_name()} @ Dr.{self.doctor.user.last_name} on {self.appointment_date} {self.start_time}"

    def clean(self):
        """Validate appointment time logic."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time.')
        if self.appointment_date and self.appointment_date < timezone.now().date():
            if self.pk is None:  # Only for new appointments
                raise ValidationError('Cannot book appointments in the past.')

    @property
    def is_cancellable(self):
        """Check if the appointment can still be cancelled (24h notice policy)."""
        if self.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED):
            return False
        appointment_dt = timezone.datetime.combine(self.appointment_date, self.start_time)
        appointment_dt = timezone.make_aware(appointment_dt)
        from django.conf import settings
        hours_until = (appointment_dt - timezone.now()).total_seconds() / 3600
        return hours_until >= getattr(settings, 'CANCELLATION_NOTICE_HOURS', 24)

    @property
    def duration_minutes(self):
        start = timezone.datetime.combine(timezone.datetime.today(), self.start_time)
        end = timezone.datetime.combine(timezone.datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)


class WalkInPatient(models.Model):
    """Walk-in patient registration (no prior appointment)."""
    STATUS = [('waiting','Waiting'),('in_progress','In Progress'),('completed','Completed'),('left','Left Without Being Seen')]

    patient_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    reason = models.TextField()
    preferred_doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='waiting')
    checked_in_at = models.DateTimeField(auto_now_add=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    assigned_appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    registered_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'appointments_walkin'
        ordering = ['checked_in_at']

    def __str__(self):
        return f"Walk-in: {self.patient_name} @ {self.checked_in_at.strftime('%H:%M')}"


class TimeOffBlock(models.Model):
    """Block a doctor's availability (vacation, conference, etc.)."""
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='time_off')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointments_timeoffblock'

    def __str__(self):
        return f"Dr. {self.doctor.user.last_name} off: {self.start_datetime.date()} – {self.end_datetime.date()}"
