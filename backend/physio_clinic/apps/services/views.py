from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from physio_clinic.apps.services.models import Service, ServiceCategory
from physio_clinic.apps.services.serializers import (
    ServiceSerializer, ServiceCategorySerializer,
    AdminServiceSerializer, AdminServiceCategorySerializer,
)
from physio_clinic.apps.accounts.permissions import IsAdmin


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


# ── Admin — full CRUD, admin role only. Mounted at /api/services/admin/ ──

class AdminServiceViewSet(viewsets.ModelViewSet):
    """
    Full CRUD over all services, active or not — the public ServiceViewSet
    above deliberately only shows active ones, so admins need their own
    queryset here to see and toggle inactive services too.
    """
    queryset = Service.objects.all().select_related('category').order_by('order', 'name')
    serializer_class = AdminServiceSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'conditions_treated']


class AdminServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = AdminServiceCategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
