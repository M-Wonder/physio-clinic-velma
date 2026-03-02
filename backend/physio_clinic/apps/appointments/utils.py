"""
Appointment availability utilities.
Handles real-time slot calculation with Redis caching.
"""
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger('physio_clinic')
SLOT_DURATION = getattr(settings, 'APPOINTMENT_DURATION_MINUTES', 60)
CACHE_TTL = 300  # 5 minutes


def get_available_slots(doctor, date_str: str) -> List[Dict]:
    """
    Calculate available appointment slots for a doctor on a given date.
    Results are cached in Redis for 5 minutes.

    Returns list of dicts: [{time: "09:00", available: True}, ...]
    """
    cache_key = f"slots:{doctor.id}:{date_str}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return []

    # Don't return past dates
    if target_date < timezone.now().date():
        return []

    # Check doctor's schedule for this weekday
    day_of_week = target_date.weekday()  # 0=Monday
    try:
        schedule = doctor.schedules.get(day_of_week=day_of_week, is_available=True)
    except Exception:
        cache.set(cache_key, [], CACHE_TTL)
        return []

    # Check time-off blocks
    from physio_clinic.apps.appointments.models import TimeOffBlock, Appointment
    is_blocked = TimeOffBlock.objects.filter(
        doctor=doctor,
        start_datetime__date__lte=target_date,
        end_datetime__date__gte=target_date,
    ).exists()
    if is_blocked:
        cache.set(cache_key, [], CACHE_TTL)
        return []

    # Get already-booked appointments
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            appointment_date=target_date,
            status__in=('scheduled', 'confirmed', 'in_progress')
        ).values_list('start_time', flat=True)
    )

    # Generate slots
    slots = []
    current = datetime.combine(target_date, schedule.start_time)
    end = datetime.combine(target_date, schedule.end_time)
    delta = timedelta(minutes=SLOT_DURATION)

    while current + delta <= end:
        slot_time = current.time()
        # Don't show past slots for today
        if target_date == timezone.now().date() and slot_time <= timezone.now().time():
            current += delta
            continue
        slots.append({
            'time': slot_time.strftime('%H:%M'),
            'available': slot_time not in booked_times,
        })
        current += delta

    cache.set(cache_key, slots, CACHE_TTL)
    return slots


def invalidate_slot_cache(doctor_id: int, date_str: str):
    """Call this after a booking to invalidate the cached slots."""
    cache.delete(f"slots:{doctor_id}:{date_str}")
