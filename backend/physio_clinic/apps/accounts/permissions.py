"""
Role-Based Access Control permissions for PhysioClinic.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('doctor', 'admin')


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('receptionist', 'admin')


class IsOwnerOrDoctorOrAdmin(BasePermission):
    """Allow access to the record owner, their doctor, or admin."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        # Check if obj has a 'user' or 'patient' attribute
        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'patient') and obj.patient.user == user:
            return True
        if user.role == 'doctor':
            return True
        return False


class IsDoctorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('doctor', 'admin', 'receptionist')
