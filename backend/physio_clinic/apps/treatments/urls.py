from django.urls import path, include
from rest_framework.routers import DefaultRouter
from physio_clinic.apps.treatments import views

router = DefaultRouter()
router.register('', views.TreatmentRecordViewSet, basename='treatment')
urlpatterns = [path('', include(router.urls))]
