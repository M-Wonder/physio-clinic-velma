from rest_framework import serializers
from physio_clinic.apps.services.models import Service, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'slug', 'category_name', 'short_description', 'description',
                  'conditions_treated', 'treatment_methods', 'session_duration_minutes',
                  'price_per_session', 'icon', 'doctor_count', 'is_active']

    def get_doctor_count(self, obj):
        return obj.doctors.filter(user__is_active=True).count()
