from rest_framework import serializers
from physio_clinic.apps.treatments.models import TreatmentRecord, TreatmentFile


class TreatmentFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentFile
        fields = ['id', 'file_url', 'file_type', 'original_filename', 'description',
                  'uploaded_at', 'file_size_bytes']
        read_only_fields = ['id', 'uploaded_at', 'file_size_bytes', 'original_filename']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class TreatmentRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.SerializerMethodField()
    files = TreatmentFileSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentRecord
        fields = [
            'id', 'patient_name', 'doctor_name', 'visit_date',
            'chief_complaint', 'diagnosis', 'treatment_given', 'treatment_plan',
            'goals', 'precautions', 'pain_level_before', 'pain_level_after',
            'functional_score', 'next_appointment_recommended', 'follow_up_notes',
            'status', 'files', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"


class TreatmentFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentFile
        fields = ['file', 'file_type', 'description']
