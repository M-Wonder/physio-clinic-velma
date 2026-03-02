from rest_framework import serializers
from physio_clinic.apps.notifications.models import NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'notification_type', 'event', 'subject', 'status', 'sent_at', 'created_at']
