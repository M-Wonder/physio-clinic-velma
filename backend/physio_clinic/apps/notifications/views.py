"""Notification preferences and logs."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from physio_clinic.apps.notifications.models import NotificationLog
from physio_clinic.apps.notifications.serializers import NotificationLogSerializer


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """Get/update notification preferences."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'email_notifications': request.user.email_notifications,
            'sms_notifications': request.user.sms_notifications,
        })

    def patch(self, request):
        user = request.user
        user.email_notifications = request.data.get('email_notifications', user.email_notifications)
        user.sms_notifications = request.data.get('sms_notifications', user.sms_notifications)
        user.save()
        return Response({'message': 'Preferences updated.', 'email_notifications': user.email_notifications, 'sms_notifications': user.sms_notifications})


class NotificationLogListView(generics.ListAPIView):
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationLog.objects.filter(user=self.request.user)[:50]
