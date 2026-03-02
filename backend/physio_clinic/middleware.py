"""
Custom Django middleware for PhysioClinic.
- Request/Response logging (audit trail)
- Performance monitoring
"""
import logging
import time
import json

logger = logging.getLogger('physio_clinic.audit')


class RequestLoggingMiddleware:
    """
    Logs all API requests with user, IP, method, path, status, and duration.
    Creates an audit trail for HIPAA/GDPR compliance.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        # Log only API requests
        if request.path.startswith('/api/'):
            duration_ms = (time.monotonic() - start_time) * 1000
            user = request.user.email if request.user.is_authenticated else 'anonymous'
            ip = self._get_client_ip(request)

            logger.info(
                'API REQUEST | user=%s ip=%s method=%s path=%s status=%d duration=%.2fms',
                user, ip, request.method, request.path,
                response.status_code, duration_ms
            )

        return response

    def _get_client_ip(self, request):
        """Extract real client IP, handling reverse proxy headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
