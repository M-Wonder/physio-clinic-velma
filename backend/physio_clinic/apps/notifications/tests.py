"""Tests for notification preferences and log endpoints."""
from django.test import TestCase
from rest_framework.test import APIClient
from physio_clinic.apps.accounts.models import User, UserRole


class NotificationPrefsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='u@test.com', password='Pass@123',
            first_name='A', last_name='B', role=UserRole.PATIENT
        )
        self.client.force_authenticate(user=self.user)

    def test_get_preferences(self):
        resp = self.client.get('/api/notifications/preferences/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('email_notifications', resp.data)

    def test_update_preferences(self):
        resp = self.client.patch('/api/notifications/preferences/',
                                 {'sms_notifications': True}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.sms_notifications)
