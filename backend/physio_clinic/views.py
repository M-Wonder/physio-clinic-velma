"""Project-level views."""
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ClinicInfoView(APIView):
    """Public clinic identity, contact details and rates (read-only)."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({
            'name': settings.CLINIC_NAME,
            'tagline': settings.CLINIC_TAGLINE,
            'phone': settings.CLINIC_PHONE,
            'whatsapp': settings.CLINIC_WHATSAPP,
            'email': settings.CLINIC_EMAIL,
            'address': settings.CLINIC_ADDRESS,
            'social_handle': settings.CLINIC_SOCIAL_HANDLE,
            'currency': settings.CLINIC_CURRENCY,
            'rates': {
                'clinic': settings.CLINIC_SESSION_FEE,
                'home': settings.CLINIC_HOME_VISIT_FEE,
            },
            'cancellation_notice_hours': settings.CANCELLATION_NOTICE_HOURS,
            'booking_advance_days': settings.BOOKING_ADVANCE_DAYS,
        })
