# domain/accounts/api/permissions.py

"""
Permissions personnalisées pour l'API accounts.
"""

from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    """
    Permission: l'utilisateur doit avoir vérifié son compte.
    """

    message = "Vous devez vérifier votre compte pour accéder à cette ressource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_verified


class IsNotVerified(BasePermission):
    """
    Permission: uniquement pour les utilisateurs non vérifiés.
    Utile pour les endpoints de vérification.
    """

    message = "Votre compte est déjà vérifié."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not request.user.is_verified


class IsOwner(BasePermission):
    """
    Permission: l'utilisateur doit être propriétaire de l'objet.
    """

    message = "Vous n'avez pas accès à cette ressource."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user
