"""
Custom authentication backend.
Allows authentication via email OR phone.
"""

import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailPhoneBackend(ModelBackend):
    """
    Authentication backend supporting email OR phone.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user by email or phone.
        """
        if username is None or password is None:
            return None

        username = username.strip()

        # Find the user
        user = self._get_user(username)

        if user is None:
            # Run hasher to avoid timing attack
            User().set_password(password)
            return None

        # Verify password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def _get_user(self, identifier: str):
        """
        Get user by email or phone.
        """
        # Try as email
        if "@" in identifier:
            try:
                return User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                return None

        # Try as phone (with different formats)
        try:
            # Exact format
            user = User.objects.filter(phone=identifier).first()
            if user:
                return user

            # Format with +224
            if not identifier.startswith("+"):
                user = User.objects.filter(phone=f"+224{identifier}").first()
                if user:
                    return user

            return None
        except Exception:
            return None

    def user_can_authenticate(self, user):
        """
        Check if user can authenticate.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None
