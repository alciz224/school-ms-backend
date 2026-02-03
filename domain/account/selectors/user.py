"""
User selectors.
"""

from django.db.models import QuerySet, Q, Count
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from domain.account.models import CustomUser


class UserSelector:
    """Selector for user queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[CustomUser]:
        """
        Get all users.

        Args:
            include_deleted: If True, include soft-deleted users

        Returns:
            QuerySet of users
        """
        if include_deleted:
            return CustomUser.all_objects.all()
        return CustomUser.objects.all()

    @staticmethod
    def get_by_id(*, user_id: int, include_deleted: bool = False) -> Optional[CustomUser]:
        """
        Get a user by ID.

        Args:
            user_id: User ID
            include_deleted: If True, include soft-deleted users

        Returns:
            User instance or None
        """
        manager = CustomUser.all_objects if include_deleted else CustomUser.objects
        return manager.filter(id=user_id).first()

    @staticmethod
    def get_by_email(*, email: str, include_deleted: bool = False) -> Optional[CustomUser]:
        """
        Get a user by email address.

        Args:
            email: Email address
            include_deleted: If True, include soft-deleted users

        Returns:
            User instance or None
        """
        manager = CustomUser.all_objects if include_deleted else CustomUser.objects
        return manager.filter(email__iexact=email.strip()).first()

    @staticmethod
    def get_by_phone(*, phone: str, include_deleted: bool = False) -> Optional[CustomUser]:
        """
        Get a user by phone number.

        Args:
            phone: Phone number
            include_deleted: If True, include soft-deleted users

        Returns:
            User instance or None
        """
        manager = CustomUser.all_objects if include_deleted else CustomUser.objects
        return manager.filter(phone=phone.strip()).first()

    @staticmethod
    def get_by_identifier(*, identifier: str, include_deleted: bool = False) -> Optional[CustomUser]:
        """
        Get a user by email or phone number.

        Args:
            identifier: Email or phone number
            include_deleted: If True, include soft-deleted users

        Returns:
            User instance or None
        """
        manager = CustomUser.all_objects if include_deleted else CustomUser.objects
        return manager.filter(
            Q(email__iexact=identifier.strip()) | Q(phone=identifier.strip())
        ).first()

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[CustomUser]:
        """
        Search users by name, email, or phone.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted users

        Returns:
            QuerySet of matching users
        """
        manager = CustomUser.all_objects if include_deleted else CustomUser.objects
        return manager.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    @staticmethod
    def get_verified_users() -> QuerySet[CustomUser]:
        """
        Get users who have verified email or phone.

        Returns:
            QuerySet of verified users
        """
        return CustomUser.objects.filter(
            Q(email_verified=True) | Q(phone_verified=True)
        )

    @staticmethod
    def get_fully_verified_users() -> QuerySet[CustomUser]:
        """
        Get users who have verified both email and phone.

        Returns:
            QuerySet of fully verified users
        """
        return CustomUser.objects.filter(
            email_verified=True,
            phone_verified=True
        )

    @staticmethod
    def get_unverified_users() -> QuerySet[CustomUser]:
        """
        Get users who haven't verified email or phone.

        Returns:
            QuerySet of unverified users
        """
        return CustomUser.objects.filter(
            email_verified=False,
            phone_verified=False
        )

    @staticmethod
    def get_active_users() -> QuerySet[CustomUser]:
        """
        Get active (non-deleted) users.

        Returns:
            QuerySet of active users
        """
        return CustomUser.objects.filter(is_active=True)

    @staticmethod
    def get_recent_users(*, days: int = 30) -> QuerySet[CustomUser]:
        """
        Get users created in the last N days.

        Args:
            days: Number of days to look back

        Returns:
            QuerySet of recent users
        """
        since = timezone.now() - timedelta(days=days)
        return CustomUser.objects.filter(date_joined__gte=since)

    @staticmethod
    def get_users_with_security_questions() -> QuerySet[CustomUser]:
        """
        Get users who have set up security questions.

        Returns:
            QuerySet of users with security questions
        """
        return CustomUser.objects.annotate(
            security_question_count=Count('security_questions')
        ).filter(security_question_count__gt=0)

    @staticmethod
    def get_users_without_security_questions() -> QuerySet[CustomUser]:
        """
        Get users who haven't set up security questions.

        Returns:
            QuerySet of users without security questions
        """
        return CustomUser.objects.annotate(
            security_question_count=Count('security_questions')
        ).filter(security_question_count=0)

    @staticmethod
    def exists_by_email(*, email: str, exclude_id: int = None) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            email: Email address to check
            exclude_id: Exclude user with this ID

        Returns:
            True if user exists with the email
        """
        queryset = CustomUser.objects.filter(email__iexact=email.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    @staticmethod
    def exists_by_phone(*, phone: str, exclude_id: int = None) -> bool:
        """
        Check if a user exists with the given phone.

        Args:
            phone: Phone number to check
            exclude_id: Exclude user with this ID

        Returns:
            True if user exists with the phone
        """
        queryset = CustomUser.objects.filter(phone=phone.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    @staticmethod
    def get_user_stats() -> dict:
        """
        Get user statistics.

        Returns:
            Dictionary with user statistics
        """
        total_users = CustomUser.objects.count()
        verified_users = UserSelector.get_verified_users().count()
        fully_verified = UserSelector.get_fully_verified_users().count()
        recent_users = UserSelector.get_recent_users().count()
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "fully_verified_users": fully_verified,
            "unverified_users": total_users - verified_users,
            "recent_users_30d": recent_users,
            "verification_rate": round((verified_users / total_users * 100) if total_users > 0 else 0, 1)
        }