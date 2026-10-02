from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from physio_clinic.apps.accounts import views

router = DefaultRouter()
router.register('doctors', views.DoctorViewSet, basename='doctor')
router.register('patients', views.PatientViewSet, basename='patient')

admin_router = DefaultRouter()
admin_router.register('doctors', views.AdminDoctorViewSet, basename='admin-doctor')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('admin/', include(admin_router.urls)),
    path('', include(router.urls)),
]
