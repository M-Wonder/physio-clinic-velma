from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from physio_clinic.apps.accounts.models import User, DoctorProfile, PatientProfile, DoctorSchedule


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff')}),
        ('Notifications', {'fields': ('email_notifications', 'sms_notifications')}),
        ('GDPR', {'fields': ('gdpr_consent', 'gdpr_consent_date', 'data_deletion_requested')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')}),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number', 'years_experience', 'is_accepting_patients']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'license_number']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'blood_type', 'primary_doctor']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
