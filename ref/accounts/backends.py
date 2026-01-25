# domain/accounts/backends.py

"""
Backend d'authentification personnalisé.
Permet l'authentification par email OU téléphone.
"""

import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailPhoneBackend(ModelBackend):
    """
    Backend d'authentification supportant email OU téléphone.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur par email ou téléphone.
        """
        if username is None or password is None:
            return None

        username = username.strip()

        # Trouver l'utilisateur
        user = self._get_user(username)

        if user is None:
            # Exécuter le hasher pour éviter le timing attack
            User().set_password(password)
            return None

        # Vérifier le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def _get_user(self, identifier: str):
        """
        Récupère l'utilisateur par email ou téléphone.
        """
        # Essayer comme email
        if "@" in identifier:
            try:
                return User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                return None

        # Essayer comme téléphone (avec différents formats)
        try:
            # Format exact
            user = User.objects.filter(phone=identifier).first()
            if user:
                return user

            # Format avec +224
            if not identifier.startswith("+"):
                user = User.objects.filter(phone=f"+224{identifier}").first()
                if user:
                    return user

            return None
        except Exception:
            return None

    def user_can_authenticate(self, user):
        """
        Vérifie si l'utilisateur peut s'authentifier.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None
