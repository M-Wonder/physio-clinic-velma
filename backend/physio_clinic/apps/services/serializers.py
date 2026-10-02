from django.utils.text import slugify
from rest_framework import serializers
from physio_clinic.apps.services.models import Service, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Public, read-only — used by the catalog pages."""
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon']


class ServiceSerializer(serializers.ModelSerializer):
    """Public, read-only — used by the catalog pages."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'slug', 'category_name', 'short_description', 'description',
                  'conditions_treated', 'treatment_methods', 'session_duration_minutes',
                  'price_per_session', 'icon', 'doctor_count', 'is_active']

    def get_doctor_count(self, obj):
        return obj.doctors.filter(user__is_active=True).count()


# ── Admin (write-capable) serializers — used only by AdminServiceViewSet /
# AdminServiceCategoryViewSet, which are gated to IsAdmin in views.py. ──

class AdminServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon']


class AdminServiceSerializer(serializers.ModelSerializer):
    """
    Full read/write Service representation for the admin panel.
    `slug` is optional on input — auto-generated from `name` when omitted,
    so the admin UI doesn't need a slug field at all.
    """
    category = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), required=False, allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'category', 'category_name', 'name', 'slug', 'short_description',
                  'description', 'conditions_treated', 'treatment_methods',
                  'session_duration_minutes', 'price_per_session', 'icon', 'image',
                  'is_active', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_slug(self, value):
        return slugify(value) if value else value

    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug'] = self._unique_slug(validated_data['name'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'slug' in validated_data and not validated_data['slug']:
            validated_data.pop('slug')
        return super().update(instance, validated_data)

    def _unique_slug(self, name):
        base = slugify(name)
        slug, n = base, 2
        while Service.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug
