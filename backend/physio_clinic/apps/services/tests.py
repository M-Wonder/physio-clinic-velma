"""Tests for the service catalog."""
from django.test import TestCase
from rest_framework.test import APIClient
from physio_clinic.apps.services.models import Service, ServiceCategory


class ServiceCatalogTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        cat = ServiceCategory.objects.create(name='Physio')
        Service.objects.create(
            name='Sports Injury', slug='sports-injury',
            short_description='For athletes',
            description='Full description',
            category=cat, is_active=True,
            session_duration_minutes=60,
        )
        Service.objects.create(
            name='Hidden Service', slug='hidden',
            short_description='Not active',
            description='Hidden',
            category=cat, is_active=False,
        )

    def test_public_service_list(self):
        """Anyone can list active services."""
        resp = self.client.get('/api/services/')
        self.assertEqual(resp.status_code, 200)
        # Only active services returned
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['name'], 'Sports Injury')

    def test_service_detail_by_slug(self):
        """Service detail accessible by slug."""
        resp = self.client.get('/api/services/sports-injury/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'Sports Injury')
