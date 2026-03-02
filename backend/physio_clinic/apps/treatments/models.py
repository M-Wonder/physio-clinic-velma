"""Treatment records and attached files."""
import uuid
import os
from django.db import models
from django.core.exceptions import ValidationError


def treatment_file_path(instance, filename):
    """Store files organized by patient and treatment."""
    ext = filename.split('.')[-1]
    return f"treatments/{instance.treatment_record.patient.user.id}/{uuid.uuid4()}.{ext}"


def validate_file_size(value):
    from django.conf import settings
    limit = getattr(settings, 'MAX_UPLOAD_SIZE', 20 * 1024 * 1024)
    if value.size > limit:
        raise ValidationError(f'File size cannot exceed {limit // 1024 // 1024}MB.')


class TreatmentRecord(models.Model):
    """A doctor's treatment record for a patient visit."""
    STATUS = [('draft','Draft'),('finalized','Finalized'),('archived','Archived')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE, related_name='treatment_records')
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='treatment_records')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_record')

    visit_date = models.DateField()
    chief_complaint = models.TextField()
    diagnosis = models.TextField()
    treatment_given = models.TextField()
    treatment_plan = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    precautions = models.TextField(blank=True)

    # Outcome measures
    pain_level_before = models.PositiveSmallIntegerField(null=True, blank=True, help_text='0-10 scale')
    pain_level_after = models.PositiveSmallIntegerField(null=True, blank=True)
    functional_score = models.CharField(max_length=50, blank=True)

    next_appointment_recommended = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'treatments_record'
        ordering = ['-visit_date']
        indexes = [models.Index(fields=['patient', 'visit_date'])]

    def __str__(self):
        return f"Treatment: {self.patient.user.last_name} on {self.visit_date}"


class TreatmentFile(models.Model):
    """File attachment for a treatment record (X-rays, scans, reports)."""
    FILE_TYPES = [('xray','X-Ray'),('scan','Scan/MRI'),('report','Lab Report'),('prescription','Prescription'),('other','Other')]

    treatment_record = models.ForeignKey(TreatmentRecord, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=treatment_file_path, validators=[validate_file_size])
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='other')
    original_filename = models.CharField(max_length=255)
    description = models.CharField(max_length=300, blank=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size_bytes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'treatments_file'

    def __str__(self):
        return f"{self.file_type}: {self.original_filename}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size_bytes = self.file.size
            self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
