from django.urls import path, include
from rest_framework.routers import DefaultRouter
from physio_clinic.apps.services import views

router = DefaultRouter()
router.register('', views.ServiceViewSet, basename='service')
router.register('categories', views.ServiceCategoryViewSet, basename='service-category')

urlpatterns = [path('', include(router.urls))]
