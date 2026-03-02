"""
Appointment Views — booking, cancellation, rescheduling, walk-ins.
Uses DB-level locking to prevent double-booking.
"""
import logging
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from physio_clinic.apps.appointments.models import Appointment, AppointmentStatus, WalkInPatient
from physio_clinic.apps.appointments.serializers import (
    AppointmentSerializer, BookAppointmentSerializer,
    RescheduleSerializer, CancelAppointmentSerializer, WalkInSerializer
)
from physio_clinic.apps.appointments.utils import get_available_slots, invalidate_slot_cache
from physio_clinic.apps.accounts.permissions import IsDoctorOrAdmin, IsReceptionist

logger = logging.getLogger('physio_clinic')


class BookingThrottle(UserRateThrottle):
    """10 booking attempts per minute per user."""
    scope = 'booking'


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for appointments.
    - Patients see only their own
    - Doctors see their patients' appointments
    - Admins/receptionists see all
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'appointment_date', 'doctor', 'appointment_type']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'reason_for_visit']
    ordering_fields = ['appointment_date', 'start_time', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related(
            'patient__user', 'doctor__user', 'service'
        )
        if user.role == 'patient':
            return qs.filter(patient__user=user)
        if user.role == 'doctor':
            return qs.filter(doctor__user=user)
        return qs  # admin/receptionist see all

    def create(self, request, *args, **kwargs):
        """Book a new appointment with concurrency protection."""
        return Response({'error': 'Use /appointments/book/ to create an appointment.'}, status=405)

    @action(detail=False, methods=['post'], throttle_classes=[BookingThrottle])
    def book(self, request):
        """
        Book an appointment. Uses select_for_update to prevent race conditions.
        Steps:
        1. Validate input (slot availability pre-check)
        2. Acquire DB lock on the slot
        3. Re-verify availability under lock
        4. Create appointment
        5. Invalidate slot cache
        6. Queue confirmation notification
        """
        serializer = BookAppointmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        doctor = data['_doctor']
        service = data['_service']
        appt_date = data['appointment_date']
        start_time = data['start_time']
        end_time = data['end_time']

        # Get or create patient profile
        from physio_clinic.apps.accounts.models import PatientProfile
        patient, _ = PatientProfile.objects.get_or_create(user=request.user)

        try:
            with transaction.atomic():
                # Pessimistic lock — block concurrent bookings for same slot
                conflicting = Appointment.objects.select_for_update().filter(
                    doctor=doctor,
                    appointment_date=appt_date,
                    start_time=start_time,
                    status__in=(AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED)
                )
                if conflicting.exists():
                    return Response(
                        {'error': 'Sorry, this slot was just booked. Please choose another time.'},
                        status=status.HTTP_409_CONFLICT
                    )

                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    service=service,
                    appointment_date=appt_date,
                    start_time=start_time,
                    end_time=end_time,
                    reason_for_visit=data.get('reason_for_visit', ''),
                    booked_by=request.user,
                    status=AppointmentStatus.SCHEDULED,
                )

            # Invalidate slot cache (outside transaction is fine)
            invalidate_slot_cache(doctor.id, appt_date.strftime('%Y-%m-%d'))

            # Queue confirmation notification asynchronously
            from physio_clinic.apps.notifications.tasks import send_appointment_confirmation
            send_appointment_confirmation.delay(str(appointment.id))

            logger.info('Appointment booked: %s by %s', appointment.id, request.user.email)
            return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception('Booking error for user %s', request.user.email)
            return Response({'error': 'Booking failed. Please try again.'}, status=500)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment (24h notice policy)."""
        appointment = self.get_object()

        if not appointment.is_cancellable:
            return Response(
                {'error': f'Appointments must be cancelled at least {getattr(__import__("django.conf", fromlist=["settings"]).settings, "CANCELLATION_NOTICE_HOURS", 24)} hours in advance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CancelAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = serializer.validated_data.get('reason', '')
        appointment.cancelled_by = request.user
        appointment.save()

        invalidate_slot_cache(appointment.doctor.id, appointment.appointment_date.strftime('%Y-%m-%d'))

        from physio_clinic.apps.notifications.tasks import send_appointment_cancellation
        send_appointment_cancellation.delay(str(appointment.id))

        logger.info('Appointment %s cancelled by %s', appointment.id, request.user.email)
        return Response({'message': 'Appointment cancelled successfully.'})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment to a new date/time."""
        old_appointment = self.get_object()
        if old_appointment.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED):
            return Response({'error': 'Only scheduled or confirmed appointments can be rescheduled.'}, status=400)

        serializer = RescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Verify new slot is available
        date_str = data['new_date'].strftime('%Y-%m-%d')
        slots = get_available_slots(old_appointment.doctor, date_str)
        time_str = data['new_time'].strftime('%H:%M')
        if not any(s['time'] == time_str and s['available'] for s in slots):
            return Response({'error': 'The requested slot is not available.'}, status=409)

        from datetime import timedelta, datetime
        duration = old_appointment.duration_minutes
        end_dt = datetime.combine(data['new_date'], data['new_time']) + timedelta(minutes=duration)

        with transaction.atomic():
            # Mark old appointment as rescheduled
            old_appointment.status = AppointmentStatus.RESCHEDULED
            old_appointment.save()

            # Create new appointment
            new_appointment = Appointment.objects.create(
                patient=old_appointment.patient,
                doctor=old_appointment.doctor,
                service=old_appointment.service,
                appointment_date=data['new_date'],
                start_time=data['new_time'],
                end_time=end_dt.time(),
                reason_for_visit=old_appointment.reason_for_visit,
                booked_by=request.user,
                rescheduled_from=old_appointment,
                status=AppointmentStatus.SCHEDULED,
            )

        invalidate_slot_cache(old_appointment.doctor.id, date_str)
        invalidate_slot_cache(old_appointment.doctor.id, old_appointment.appointment_date.strftime('%Y-%m-%d'))

        from physio_clinic.apps.notifications.tasks import send_appointment_confirmation
        send_appointment_confirmation.delay(str(new_appointment.id))

        return Response(AppointmentSerializer(new_appointment).data, status=201)

    @action(detail=False, methods=['get'])
    def slots(self, request):
        """Get available slots for a doctor on a specific date."""
        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')
        if not doctor_id or not date_str:
            return Response({'error': 'doctor_id and date are required.'}, status=400)
        from physio_clinic.apps.accounts.models import DoctorProfile
        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor not found.'}, status=404)
        slots = get_available_slots(doctor, date_str)
        return Response({'doctor_id': int(doctor_id), 'date': date_str, 'slots': slots})

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsDoctorOrAdmin])
    def update_notes(self, request, pk=None):
        """Doctor updates their notes after/during appointment."""
        appointment = self.get_object()
        notes = request.data.get('doctor_notes', '')
        appointment.doctor_notes = notes
        if request.data.get('status'):
            appointment.status = request.data['status']
        appointment.save()
        return Response(AppointmentSerializer(appointment).data)


class WalkInViewSet(viewsets.ModelViewSet):
    """Manage walk-in patient queue."""
    serializer_class = WalkInSerializer
    filterset_fields = ['status', 'preferred_doctor']
    ordering = ['checked_in_at']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsDoctorOrAdmin()]

    def get_queryset(self):
        return WalkInPatient.objects.select_related('preferred_doctor__user', 'registered_by').filter(
            checked_in_at__date=timezone.now().date()
        )

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)
