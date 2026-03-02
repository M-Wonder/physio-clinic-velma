"""
Accounts Views — Auth, Doctor/Patient profiles
"""
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from physio_clinic.apps.accounts.models import DoctorProfile, PatientProfile, UserRole
from physio_clinic.apps.accounts.serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer,
    UserSerializer, DoctorProfileSerializer, PatientProfileSerializer
)
from physio_clinic.apps.accounts.permissions import IsAdmin, IsOwnerOrDoctorOrAdmin

User = get_user_model()
logger = logging.getLogger('physio_clinic')


class RegisterView(generics.CreateAPIView):
    """Patient self-registration endpoint."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Auto-issue JWT tokens on registration
        refresh = RefreshToken.for_user(user)
        logger.info('New patient registered: %s', user.email)
        return Response({
            'message': 'Registration successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """JWT login with extra user info."""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(generics.GenericAPIView):
    """Blacklist refresh token on logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token required.'}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info('User logged out: %s', request.user.email)
            return Response({'message': 'Logged out successfully.'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class MeView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated user's own profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve doctor profiles."""
    queryset = DoctorProfile.objects.filter(
        user__is_active=True
    ).select_related('user').prefetch_related('specialties', 'schedules')
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['is_accepting_patients']
    search_fields = ['user__first_name', 'user__last_name', 'specialties__name']

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Return available time slots for a doctor for a given date range."""
        from physio_clinic.apps.appointments.utils import get_available_slots
        doctor = self.get_object()
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date parameter required (YYYY-MM-DD)'}, status=400)
        slots = get_available_slots(doctor, date_str)
        return Response({'doctor_id': doctor.id, 'date': date_str, 'slots': slots})


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD for patient profiles. Patients can only access their own."""
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrDoctorOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'doctor', 'receptionist'):
            return PatientProfile.objects.select_related('user', 'primary_doctor__user').all()
        return PatientProfile.objects.filter(user=user)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get/update the current patient's own profile."""
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def request_data_deletion(self, request):
        """GDPR right to erasure — mark account for deletion."""
        user = request.user
        user.data_deletion_requested = True
        user.save()
        logger.info('GDPR deletion requested by user %s', user.email)
        return Response({'message': 'Data deletion request submitted. You will be notified within 30 days.'})

    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """GDPR data portability — export all personal data."""
        user = request.user
        try:
            profile = user.patient_profile
        except PatientProfile.DoesNotExist:
            return Response({'error': 'Patient profile not found'}, status=404)

        export = {
            'personal_info': {
                'email': user.email,
                'name': user.get_full_name(),
                'phone': user.phone_number,
                'date_joined': user.date_joined.isoformat(),
            },
            'medical_profile': {
                'date_of_birth': str(profile.date_of_birth),
                'blood_type': profile.blood_type,
                'allergies': profile.allergies,
                'medications': profile.current_medications,
            }
        }
        return Response(export)
