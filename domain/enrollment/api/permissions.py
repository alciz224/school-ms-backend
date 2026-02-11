"""Portal-based permissions for Enrollment domain.

Since current_role is stored in session (not in the User model),
we read it from request.session to determine access.
"""

from rest_framework.permissions import BasePermission


class HasPortalRole(BasePermission):
    """
    Base permission that checks if user has one of the required roles in session.
    
    Usage in views:
        permission_classes = [HasPortalRole]
        required_roles = ['SCHOOL_ADMIN', 'STAFF']
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Read current_role from session
        current_role = request.session.get("current_role")
        if not current_role:
            return False

        # Check if view defines required roles
        required_roles = getattr(view, "required_roles", None)
        if required_roles is None:
            # No role restriction: allow any authenticated user with a role
            return True

        return current_role in required_roles


class IsSchoolStaffOrAdmin(BasePermission):
    """Shortcut: only SCHOOL_ADMIN or STAFF can access."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        current_role = request.session.get("current_role")
        return current_role in ["SCHOOL_ADMIN", "STAFF"]


class IsTeacher(BasePermission):
    """Shortcut: only TEACHER role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        current_role = request.session.get("current_role")
        return current_role == "TEACHER"


class IsStudent(BasePermission):
    """Shortcut: only STUDENT role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        current_role = request.session.get("current_role")
        return current_role == "STUDENT"


class IsParent(BasePermission):
    """Shortcut: only PARENT role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        current_role = request.session.get("current_role")
        return current_role == "PARENT"
