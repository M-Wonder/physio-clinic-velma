from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class ClinicInfoTest(TestCase):
    def test_public_clinic_info(self):
        resp = APIClient().get('/api/clinic/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'Neuromotion Physiotherapy Clinic')
        self.assertEqual(resp.data['currency'], 'KES')
        self.assertEqual(resp.data['rates'], {'clinic': 4500, 'home': 5500})

    @override_settings(CLINIC_SESSION_FEE=5000, CLINIC_PHONE='+254 711 000 000')
    def test_values_come_from_settings(self):
        data = APIClient().get('/api/clinic/').data
        self.assertEqual(data['rates']['clinic'], 5000)
        self.assertEqual(data['phone'], '+254 711 000 000')
