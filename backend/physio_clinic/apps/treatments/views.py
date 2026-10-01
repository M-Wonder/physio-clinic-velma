"""Treatment record views."""
import logging
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from physio_clinic.apps.treatments.models import TreatmentRecord, TreatmentFile
from physio_clinic.apps.treatments.serializers import TreatmentRecordSerializer, TreatmentFileUploadSerializer
from physio_clinic.apps.accounts.permissions import IsDoctor, IsOwnerOrDoctorOrAdmin

logger = logging.getLogger('physio_clinic')


class TreatmentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentRecordSerializer
    filterset_fields = ['status', 'visit_date', 'doctor']
    search_fields = ['chief_complaint', 'diagnosis', 'patient__user__last_name']
    ordering_fields = ['visit_date', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated(), IsOwnerOrDoctorOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        qs = TreatmentRecord.objects.select_related(
            'patient__user', 'doctor__user', 'appointment'
        ).prefetch_related('files')
        if user.role == 'patient':
            return qs.filter(patient__user=user)
        if user.role == 'doctor':
            return qs.filter(doctor__user=user)
        return qs

    def perform_create(self, serializer):
        doctor = self.request.user.doctor_profile
        serializer.save(doctor=doctor)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_file(self, request, pk=None):
        """Attach a file to a treatment record."""
        record = self.get_object()
        serializer = TreatmentFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.save(
            treatment_record=record,
            uploaded_by=request.user,
        )
        logger.info('File uploaded to treatment %s by %s', record.id, request.user.email)
        from physio_clinic.apps.treatments.serializers import TreatmentFileSerializer
        return Response(TreatmentFileSerializer(file, context={'request': request}).data, status=201)

    @action(detail=True, methods=['delete'], url_path='files/(?P<file_id>[^/.]+)')
    def delete_file(self, request, pk=None, file_id=None):
        record = self.get_object()
        try:
            file = record.files.get(id=file_id)
            file.file.delete(save=False)
            file.delete()
            return Response(status=204)
        except TreatmentFile.DoesNotExist:
            return Response({'error': 'File not found.'}, status=404)


class TreatmentFileDownloadView(APIView):
    """
    Streams a treatment file via nginx X-Accel-Redirect after an ownership
    check. nginx serves /var/www/media/ only under the `internal` location
    /protected-media/, so this view is the ONLY way to reach a file — there
    is no public URL for it.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tfile = get_object_or_404(
            TreatmentFile.objects.select_related(
                'treatment_record__patient__user', 'treatment_record__doctor__user'
            ),
            pk=pk,
        )
        record, user = tfile.treatment_record, request.user
        allowed = (
            user.role == 'admin'
            or record.patient.user_id == user.id
            or record.doctor.user_id == user.id
        )
        if not allowed:
            # 404, not 403 — don't confirm to an unauthorized user that this
            # record even exists.
            raise Http404

        response = HttpResponse(content_type='application/octet-stream')
        response['X-Accel-Redirect'] = f'/protected-media/{tfile.file.name}'
        response['Content-Disposition'] = f'attachment; filename="{tfile.original_filename}"'
        return response
