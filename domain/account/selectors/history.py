"""
History selectors (LoginAttempt, PhoneHistory).
"""

from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from domain.account.models import LoginAttempt, PhoneHistory, CustomUser


class LoginAttemptSelector:
    """Selector for login attempt queries."""

    @staticmethod
    def for_user(*, user: CustomUser) -> QuerySet[LoginAttempt]:
        """
        Get all login attempts for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of login attempts ordered by date descending
        """
        return LoginAttempt.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def recent_attempts(*, user: CustomUser, hours: int = 24) -> QuerySet[LoginAttempt]:
        """
        Get recent login attempts for a user.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            QuerySet of recent login attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return LoginAttempt.objects.filter(
            user=user,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def successful_attempts(*, user: CustomUser) -> QuerySet[LoginAttempt]:
        """
        Get successful login attempts for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of successful login attempts
        """
        return LoginAttempt.objects.filter(
            user=user,
            success=True
        ).order_by('-created_at')

    @staticmethod
    def failed_attempts(*, user: CustomUser, hours: int = 24) -> QuerySet[LoginAttempt]:
        """
        Get failed login attempts for a user in the last N hours.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            QuerySet of failed login attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return LoginAttempt.objects.filter(
            user=user,
            success=False,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def get_failed_attempt_count(*, user: CustomUser, hours: int = 24) -> int:
        """
        Get the number of failed login attempts in the last N hours.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            Number of failed attempts
        """
        return LoginAttemptSelector.failed_attempts(user=user, hours=hours).count()

    @staticmethod
    def by_ip_address(*, ip_address: str, hours: int = 24) -> QuerySet[LoginAttempt]:
        """
        Get login attempts by IP address.

        Args:
            ip_address: IP address
            hours: Number of hours to look back

        Returns:
            QuerySet of login attempts from the IP
        """
        since = timezone.now() - timedelta(hours=hours)
        return LoginAttempt.objects.filter(
            ip_address=ip_address,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def get_last_successful_login(*, user: CustomUser) -> Optional[LoginAttempt]:
        """
        Get the last successful login for a user.

        Args:
            user: User instance

        Returns:
            Last successful LoginAttempt instance or None
        """
        return LoginAttempt.objects.filter(
            user=user,
            success=True
        ).order_by('-created_at').first()

    @staticmethod
    def get_login_stats(*, user: CustomUser, days: int = 30) -> dict:
        """
        Get login attempt statistics for a user.

        Args:
            user: User instance
            days: Number of days to analyze

        Returns:
            Dictionary with login statistics
        """
        since = timezone.now() - timedelta(days=days)
        attempts = LoginAttempt.objects.filter(
            user=user,
            created_at__gte=since
        )
        
        total_attempts = attempts.count()
        successful_attempts = attempts.filter(success=True).count()
        
        return {
            "total_attempts": total_attempts,
            "successful_logins": successful_attempts,
            "failed_attempts": total_attempts - successful_attempts,
            "success_rate": round((successful_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1),
            "last_login": LoginAttemptSelector.get_last_successful_login(user=user),
            "last_attempt": attempts.order_by('-created_at').first()
        }


class PhoneHistorySelector:
    """Selector for phone history queries."""

    @staticmethod
    def for_user(*, user: CustomUser) -> QuerySet[PhoneHistory]:
        """
        Get all phone number changes for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of phone history ordered by date descending
        """
        return PhoneHistory.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_previous_phone(*, user: CustomUser) -> Optional[PhoneHistory]:
        """
        Get the most recent previous phone number for a user.

        Args:
            user: User instance

        Returns:
            Most recent PhoneHistory instance or None
        """
        return PhoneHistory.objects.filter(user=user).order_by('-created_at').first()

    @staticmethod
    def has_used_phone(*, user: CustomUser, phone: str) -> bool:
        """
        Check if a user has used a specific phone number before.

        Args:
            user: User instance
            phone: Phone number to check

        Returns:
            True if user has used this phone number
        """
        # Check current phone
        if user.phone == phone:
            return True
        
        # Check history
        return PhoneHistory.objects.filter(
            user=user,
            old_phone=phone
        ).exists()

    @staticmethod
    def get_phone_change_count(*, user: CustomUser, days: int = 365) -> int:
        """
        Get the number of phone changes in the last N days.

        Args:
            user: User instance
            days: Number of days to look back

        Returns:
            Number of phone changes
        """
        since = timezone.now() - timedelta(days=days)
        return PhoneHistory.objects.filter(
            user=user,
            created_at__gte=since
        ).count()

    @staticmethod
    def recent_changes(*, user: CustomUser, days: int = 30) -> QuerySet[PhoneHistory]:
        """
        Get recent phone number changes.

        Args:
            user: User instance
            days: Number of days to look back

        Returns:
            QuerySet of recent phone changes
        """
        since = timezone.now() - timedelta(days=days)
        return PhoneHistory.objects.filter(
            user=user,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def get_phone_timeline(*, user: CustomUser) -> list:
        """
        Get a timeline of all phone numbers used by the user.

        Args:
            user: User instance

        Returns:
            List of phone numbers in chronological order (oldest to newest)
        """
        history = PhoneHistory.objects.filter(user=user).order_by('created_at')
        
        timeline = []
        for record in history:
            timeline.append({
                "phone": record.old_phone,
                "changed_at": record.created_at,
                "reason": record.reason if hasattr(record, 'reason') else None
            })
        
        # Add current phone
        if user.phone:
            timeline.append({
                "phone": user.phone,
                "changed_at": history.last().created_at if history.exists() else user.date_joined,
                "reason": "current"
            })
        
        return timeline