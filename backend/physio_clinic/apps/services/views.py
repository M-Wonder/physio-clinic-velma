from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from physio_clinic.apps.services.models import Service, ServiceCategory
from physio_clinic.apps.services.serializers import ServiceSerializer, ServiceCategorySerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Public service catalog."""
    queryset = Service.objects.filter(is_active=True).select_related('category')
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category']
    search_fields = ['name', 'description', 'conditions_treated']
    lookup_field = 'slug'


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
