"""Permissions par rôle de portail.

Le rôle actif de l'utilisateur est stocké en session sous la clé
`ACTIVE_ROLE_SESSION_KEY` (= "active_role"), avec une valeur de
`UserRole` en lowercase (ex : "school_admin", "teacher", "student").

Les superusers Django sont toujours autorisés (bypass).
"""

from rest_framework.permissions import BasePermission

from domain.account.constants import ACTIVE_ROLE_SESSION_KEY, UserRole


def _current_role(request) -> str | None:
    return request.session.get(ACTIVE_ROLE_SESSION_KEY)


class HasPortalRole(BasePermission):
    """
    Permission générique : autorise si le rôle actif fait partie de
    `view.required_roles`.

    Usage :
        permission_classes = [HasPortalRole]
        required_roles = [UserRole.SCHOOL_ADMIN, UserRole.ADMIN]
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        current_role = _current_role(request)
        if not current_role:
            return False

        required_roles = getattr(view, "required_roles", None)
        if required_roles is None:
            return True

        return current_role in required_roles


class IsSchoolStaffOrAdmin(BasePermission):
    """Réservé au portail école : school_admin, admin (ou superuser)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        return _current_role(request) in {
            UserRole.SCHOOL_ADMIN,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        }


class IsTeacher(BasePermission):
    """Portail enseignant."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return _current_role(request) == UserRole.TEACHER


class IsStudent(BasePermission):
    """Portail élève."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return _current_role(request) == UserRole.STUDENT


class IsParent(BasePermission):
    """Portail parent."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return _current_role(request) == UserRole.PARENT
