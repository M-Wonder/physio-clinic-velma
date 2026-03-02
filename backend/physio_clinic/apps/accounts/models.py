"""
Accounts Models — PhysioClinic
User, DoctorProfile, PatientProfile, DoctorSchedule
"""
import logging
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from physio_clinic.apps.accounts.encryption import EncryptedField

logger = logging.getLogger('physio_clinic')


class UserRole(models.TextChoices):
    PATIENT = 'patient', 'Patient'
    DOCTOR = 'doctor', 'Doctor'
    RECEPTIONIST = 'receptionist', 'Receptionist'
    ADMIN = 'admin', 'Admin'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with role-based access."""
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PATIENT)
    phone_number = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)

    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    # GDPR compliance
    gdpr_consent = models.BooleanField(default=False)
    gdpr_consent_date = models.DateTimeField(null=True, blank=True)
    data_deletion_requested = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        indexes = [models.Index(fields=['role', 'is_active'])]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_doctor(self):
        return self.role == UserRole.DOCTOR

    @property
    def is_patient(self):
        return self.role == UserRole.PATIENT


class DoctorProfile(models.Model):
    """Extended profile for doctors."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialties = models.ManyToManyField('services.Service', blank=True, related_name='doctors')
    license_number = models.CharField(max_length=50, unique=True)
    qualifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avatar = models.ImageField(upload_to='doctors/avatars/', null=True, blank=True)
    is_accepting_patients = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_doctor_profile'

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class PatientProfile(models.Model):
    """Extended profile for patients. Sensitive fields are encrypted."""
    BLOOD_TYPES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]
    GENDER_CHOICES = [('M','Male'),('F','Female'),('O','Other'),('P','Prefer not to say')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True)

    # AES-256 encrypted PII
    medical_history = EncryptedField(blank=True)
    allergies = EncryptedField(blank=True)
    current_medications = EncryptedField(blank=True)
    emergency_contact_name = EncryptedField(blank=True)
    emergency_contact_phone = EncryptedField(blank=True)

    insurance_provider = models.CharField(max_length=200, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    primary_doctor = models.ForeignKey(
        DoctorProfile, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='primary_patients'
    )
    avatar = models.ImageField(upload_to='patients/avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_patient_profile'

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

    @property
    def age(self):
        if self.date_of_birth:
            return (timezone.now().date() - self.date_of_birth).days // 365
        return None


class DoctorSchedule(models.Model):
    """Weekly recurring schedule for a doctor."""
    DAYS = [(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=8)

    class Meta:
        db_table = 'accounts_doctor_schedule'
        unique_together = ('doctor', 'day_of_week')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"Dr. {self.doctor.user.last_name} - {self.get_day_of_week_display()}"
