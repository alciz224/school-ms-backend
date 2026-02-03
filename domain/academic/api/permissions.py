"""Permissions for Academic domain API."""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit master data.
    
    Read-only access is allowed for all authenticated users.
    Only admins can create, update, or delete.
    """

    def has_permission(self, request, view):
        """Check if user has permission."""
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff
