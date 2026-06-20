"""
Admin user management service.

Handles user CRUD for the super-admin portal.
Uses generate random password for new users; password reset flow handles activation.
"""

import secrets
import string

from domain.account.models import CustomUser


class AdminUserService:
    """Service for admin user management (super-admin portal)."""

    @staticmethod
    def create_user(*, email, phone, first_name, last_name, is_active, is_staff, user):
        """Create a new user with a random password.

        Returns (user, password) so the creator can share credentials.
        """
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
            for _ in range(20)
        )
        user_obj = CustomUser.objects.create_user(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=is_active,
            is_staff=is_staff,
        )
        return user_obj, password

    @staticmethod
    def update_user(*, target_user, data, updater):
        """Update user fields.

        Only the fields present in data are applied.
        """
        allowed_fields = ["email", "phone", "first_name", "last_name", "is_active", "is_staff"]
        update_fields = []
        for field in allowed_fields:
            if field in data:
                setattr(target_user, field, data[field])
                update_fields.append(field)
        if update_fields:
            target_user.save(update_fields=update_fields)
        return target_user

    @staticmethod
    def delete_user(*, target_user, deleter):
        """Soft-delete a user by deactivating them."""
        target_user.is_active = False
        target_user.save(update_fields=["is_active"])
