from django.urls import path, include
from rest_framework.routers import DefaultRouter
from physio_clinic.apps.services import views

router = DefaultRouter()
router.register('', views.ServiceViewSet, basename='service')
router.register('categories', views.ServiceCategoryViewSet, basename='service-category')

admin_router = DefaultRouter()
admin_router.register('', views.AdminServiceViewSet, basename='admin-service')
admin_router.register('categories', views.AdminServiceCategoryViewSet, basename='admin-service-category')

urlpatterns = [
    # Admin routes must come before the public router's catch-all ''
    # registration, or DRF's router would try to resolve "admin" as a
    # service slug and 404 before ever reaching these.
    path('admin/', include(admin_router.urls)),
    path('', include(router.urls)),
]
