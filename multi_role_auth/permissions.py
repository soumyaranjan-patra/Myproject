"""
Custom permission classes for multi-role auth.
IsVerifiedProfessor: only approved professors can access protected data.
"""
from rest_framework import permissions

from .models import Role, VerificationStatus


class IsVerifiedProfessor(permissions.BasePermission):
    """
    Allows access only to users who are:
    - role PROFESSOR
    - verification_status APPROVED
    - is_active True
    """

    message = "Only verified (approved) professors can access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        return (
            user.role == Role.PROFESSOR
            and user.verification_status == VerificationStatus.APPROVED
            and user.is_active
        )


class IsAdminOrVerifiedProfessor(permissions.BasePermission):
    """Allow ADMIN or verified PROFESSOR."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        if user.role == Role.ADMIN and user.is_staff:
            return True
        return (
            user.role == Role.PROFESSOR
            and user.verification_status == VerificationStatus.APPROVED
            and user.is_active
        )
