"""Custom DRF exception handler for consistent error responses."""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('physio_clinic')


def custom_exception_handler(exc, context):
    """
    Returns errors in a consistent format:
    {
        "error": "Human readable message",
        "detail": {...},
        "code": "error_code"
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': _get_error_message(response.data),
            'detail': response.data,
            'status_code': response.status_code,
        }
        return Response(error_data, status=response.status_code)

    # Unhandled exceptions — return 500
    logger.exception('Unhandled exception in %s', context.get('view'))
    return Response(
        {'error': 'An internal server error occurred.', 'status_code': 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _get_error_message(data):
    """Extract a human-readable error message from DRF error data."""
    if isinstance(data, dict):
        for key in ('detail', 'non_field_errors', 'error'):
            if key in data:
                val = data[key]
                return str(val[0]) if isinstance(val, list) else str(val)
        # Return first field error
        for key, val in data.items():
            return f"{key}: {val[0] if isinstance(val, list) else val}"
    if isinstance(data, list):
        return str(data[0])
    return str(data)
