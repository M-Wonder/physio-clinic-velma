from django.urls import path, include
from rest_framework.routers import DefaultRouter
from physio_clinic.apps.treatments import views

router = DefaultRouter()
router.register('', views.TreatmentRecordViewSet, basename='treatment')

urlpatterns = [
    path('files/<int:pk>/download/', views.TreatmentFileDownloadView.as_view(), name='treatment-file-download'),
    path('', include(router.urls)),
]
