"""Notification log model."""
from django.db import models


class NotificationLog(models.Model):
    TYPE = [('email','Email'),('sms','SMS'),('push','Push')]
    EVENT = [('confirmation','Confirmation'),('reminder','Reminder'),('cancellation','Cancellation'),('rescheduled','Rescheduled'),('other','Other')]
    STATUS = [('pending','Pending'),('sent','Sent'),('failed','Failed')]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=TYPE)
    event = models.CharField(max_length=20, choices=EVENT)
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_log'
        ordering = ['-created_at']
