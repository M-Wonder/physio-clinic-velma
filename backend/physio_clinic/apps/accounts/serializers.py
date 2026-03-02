"""
Accounts Serializers — Registration, Login, Profiles
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from physio_clinic.apps.accounts.models import DoctorProfile, PatientProfile, DoctorSchedule, UserRole

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Patient self-registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    gdpr_consent = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password2', 'gdpr_consent']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if not attrs.get('gdpr_consent'):
            raise serializers.ValidationError({'gdpr_consent': 'You must accept the privacy policy.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            role=UserRole.PATIENT,
            gdpr_consent=True,
            gdpr_consent_date=timezone.now(),
        )
        # Auto-create patient profile
        PatientProfile.objects.create(user=user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login — adds user info to token response."""
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': self.user.get_full_name(),
            'role': self.user.role,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    """Public user info."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone_number',
                  'email_notifications', 'sms_notifications', 'date_joined']
        read_only_fields = ['id', 'email', 'role', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()


class DoctorScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorSchedule
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_available', 'max_patients']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Doctor profile with schedule and specialties."""
    user = UserSerializer(read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)
    specialty_names = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'specialty_names', 'license_number', 'qualifications',
                  'bio', 'years_experience', 'consultation_fee', 'avatar_url',
                  'is_accepting_patients', 'schedules']

    def get_specialty_names(self, obj):
        return list(obj.specialties.values_list('name', flat=True))

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class PatientProfileSerializer(serializers.ModelSerializer):
    """Patient profile — sensitive fields only visible to owner/doctor/admin."""
    user = UserSerializer(read_only=True)
    age = serializers.IntegerField(read_only=True)
    primary_doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = ['id', 'user', 'date_of_birth', 'age', 'gender', 'blood_type',
                  'medical_history', 'allergies', 'current_medications',
                  'emergency_contact_name', 'emergency_contact_phone',
                  'insurance_provider', 'insurance_policy_number',
                  'primary_doctor_name', 'created_at']

    def get_primary_doctor_name(self, obj):
        if obj.primary_doctor:
            return f"Dr. {obj.primary_doctor.user.get_full_name()}"
        return None
