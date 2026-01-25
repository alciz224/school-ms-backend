"""
Custom permissions for the accounts API.
"""

from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    """
    Permission: user must have verified their account.
    """

    message = "You must verify your account to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_verified


class IsNotVerified(BasePermission):
    """
    Permission: only for unverified users.
    Useful for verification endpoints.
    """

    message = "Your account is already verified."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not request.user.is_verified


class IsOwner(BasePermission):
    """
    Permission: user must be the owner of the object.
    """

    message = "You do not have access to this resource."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class HasSecurityQuestions(BasePermission):
    """
    Permission: user must have configured security questions.
    """

    message = "You must configure security questions first."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_security_questions
