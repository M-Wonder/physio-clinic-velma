from django.urls import path, include
from rest_framework.routers import DefaultRouter
from physio_clinic.apps.appointments import views

router = DefaultRouter()
router.register('walkins', views.WalkInViewSet, basename='walkin')
router.register('', views.AppointmentViewSet, basename='appointment')

urlpatterns = [path('', include(router.urls))]
