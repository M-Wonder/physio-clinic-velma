"""Appointment serializers."""
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus, WalkInPatient, TimeOffBlock
from physio_clinic.apps.appointments.utils import get_available_slots


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source='service.name', read_only=True)
    is_cancellable = serializers.BooleanField(read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_name', 'doctor_name', 'service_name',
            'appointment_date', 'start_time', 'end_time',
            'status', 'appointment_type', 'reason_for_visit',
            'doctor_notes', 'is_cancellable', 'duration_minutes',
            'reminder_sent', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'doctor_notes', 'reminder_sent']

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"


class BookAppointmentSerializer(serializers.Serializer):
    """Validates a new appointment booking request."""
    doctor_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    appointment_date = serializers.DateField()
    start_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    reason_for_visit = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_appointment_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError('Cannot book in the past.')
        max_days = getattr(settings, 'BOOKING_ADVANCE_DAYS', 30)
        if (value - timezone.now().date()).days > max_days:
            raise serializers.ValidationError(f'Cannot book more than {max_days} days in advance.')
        return value

    def validate(self, attrs):
        from physio_clinic.apps.accounts.models import DoctorProfile
        from physio_clinic.apps.services.models import Service
        from datetime import timedelta

        # Validate doctor exists
        try:
            doctor = DoctorProfile.objects.get(id=attrs['doctor_id'], user__is_active=True)
        except DoctorProfile.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Doctor not found.'})

        # Validate service
        try:
            service = Service.objects.get(id=attrs['service_id'], is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError({'service_id': 'Service not found.'})

        # Check slot availability
        date_str = attrs['appointment_date'].strftime('%Y-%m-%d')
        slots = get_available_slots(doctor, date_str)
        slot_time_str = attrs['start_time'].strftime('%H:%M')
        available_slot = next((s for s in slots if s['time'] == slot_time_str and s['available']), None)
        if not available_slot:
            raise serializers.ValidationError({'start_time': 'This time slot is not available.'})

        # Compute end time
        duration = service.session_duration_minutes or settings.APPOINTMENT_DURATION_MINUTES
        from datetime import datetime
        start_dt = datetime.combine(attrs['appointment_date'], attrs['start_time'])
        end_dt = start_dt + timedelta(minutes=duration)
        attrs['end_time'] = end_dt.time()
        attrs['_doctor'] = doctor
        attrs['_service'] = service
        return attrs


class RescheduleSerializer(serializers.Serializer):
    new_date = serializers.DateField()
    new_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    reason = serializers.CharField(required=False, allow_blank=True)


class CancelAppointmentSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=300)


class WalkInSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalkInPatient
        fields = ['id', 'patient_name', 'phone_number', 'reason', 'preferred_doctor',
                  'status', 'checked_in_at', 'seen_at', 'notes']
        read_only_fields = ['id', 'status', 'checked_in_at', 'seen_at']
