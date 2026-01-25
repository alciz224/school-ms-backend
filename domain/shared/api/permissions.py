"""
Custom permission classes.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission that only allows owners of an object to access it.

    Requires the view to have a `get_owner` method or the object
    to have a `user` or `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Check if view has custom owner method
        if hasattr(view, "get_owner"):
            owner = view.get_owner(obj)
        elif hasattr(obj, "user"):
            owner = obj.user
        elif hasattr(obj, "owner"):
            owner = obj.owner
        else:
            return False

        return owner == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows owners or admins to access an object.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_staff:
            return True

        # Check ownership
        if hasattr(view, "get_owner"):
            owner = view.get_owner(obj)
        elif hasattr(obj, "user"):
            owner = obj.user
        elif hasattr(obj, "owner"):
            owner = obj.owner
        else:
            return False

        return owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows read-only access to anyone,
    but only admins can modify.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admins
        return request.user and request.user.is_staff


class IsVerified(permissions.BasePermission):
    """
    Permission that only allows verified users.

    A user is verified if their email OR phone is verified.
    """

    message = "Your account must be verified to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return getattr(request.user, "is_verified", False)


class IsEmailVerified(permissions.BasePermission):
    """
    Permission that requires email verification.
    """

    message = "Your email must be verified to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return getattr(request.user, "email_verified", False)


class IsPhoneVerified(permissions.BasePermission):
    """
    Permission that requires phone verification.
    """

    message = "Your phone must be verified to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return getattr(request.user, "phone_verified", False)


class IsActiveUser(permissions.BasePermission):
    """
    Permission that only allows active users.
    """

    message = "Your account is not active."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_active
