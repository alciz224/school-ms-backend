"""
Security question selectors.
"""

from django.db.models import QuerySet, Count
from django.utils import timezone
from datetime import timedelta
from typing import Optional, List

from domain.account.models import SecurityQuestion, SecurityQuestionAttempt, CustomUser


class SecurityQuestionSelector:
    """Selector for security question queries."""

    @staticmethod
    def get_by_id(*, question_id: str) -> Optional[SecurityQuestion]:
        """
        Get a security question by ID.

        Args:
            question_id: Question UUID

        Returns:
            SecurityQuestion instance or None
        """
        return SecurityQuestion.objects.filter(id=question_id).first()

    @staticmethod
    def for_user(*, user: CustomUser) -> QuerySet[SecurityQuestion]:
        """
        Get security questions for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of user's security questions ordered by order
        """
        return SecurityQuestion.objects.filter(user=user).order_by('order')

    @staticmethod
    def for_user_by_order(*, user: CustomUser, order: int) -> Optional[SecurityQuestion]:
        """
        Get a specific security question by order for a user.

        Args:
            user: User instance
            order: Question order (1, 2, or 3)

        Returns:
            SecurityQuestion instance or None
        """
        return SecurityQuestion.objects.filter(user=user, order=order).first()

    @staticmethod
    def get_user_question_count(*, user: CustomUser) -> int:
        """
        Get the number of security questions set by a user.

        Args:
            user: User instance

        Returns:
            Number of security questions
        """
        return SecurityQuestion.objects.filter(user=user).count()

    @staticmethod
    def has_complete_setup(*, user: CustomUser) -> bool:
        """
        Check if user has completed security questions setup (3 questions).

        Args:
            user: User instance

        Returns:
            True if user has 3 security questions
        """
        return SecurityQuestionSelector.get_user_question_count(user=user) >= 3

    @staticmethod
    def get_available_orders_for_user(*, user: CustomUser) -> List[int]:
        """
        Get available order positions for a user.

        Args:
            user: User instance

        Returns:
            List of available order positions (1, 2, 3)
        """
        used_orders = list(
            SecurityQuestion.objects.filter(user=user).values_list('order', flat=True)
        )
        return [order for order in [1, 2, 3] if order not in used_orders]

    @staticmethod
    def get_predefined_questions() -> List[str]:
        """
        Get the list of predefined security questions.

        Returns:
            List of predefined questions
        """
        return SecurityQuestion.get_predefined_questions()


class SecurityQuestionAttemptSelector:
    """Selector for security question attempt queries."""

    @staticmethod
    def for_user(*, user: CustomUser) -> QuerySet[SecurityQuestionAttempt]:
        """
        Get security question attempts for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of attempts ordered by date descending
        """
        return SecurityQuestionAttempt.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def recent_attempts(*, user: CustomUser, hours: int = 24) -> QuerySet[SecurityQuestionAttempt]:
        """
        Get recent security question attempts for a user.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            QuerySet of recent attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return SecurityQuestionAttempt.objects.filter(
            user=user,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def successful_attempts(*, user: CustomUser) -> QuerySet[SecurityQuestionAttempt]:
        """
        Get successful security question attempts for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of successful attempts
        """
        return SecurityQuestionAttempt.objects.filter(
            user=user,
            success=True
        ).order_by('-created_at')

    @staticmethod
    def failed_attempts(*, user: CustomUser, hours: int = 24) -> QuerySet[SecurityQuestionAttempt]:
        """
        Get failed security question attempts for a user in the last N hours.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            QuerySet of failed attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return SecurityQuestionAttempt.objects.filter(
            user=user,
            success=False,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def get_failed_attempt_count(*, user: CustomUser, hours: int = 24) -> int:
        """
        Get the number of failed attempts in the last N hours.

        Args:
            user: User instance
            hours: Number of hours to look back

        Returns:
            Number of failed attempts
        """
        return SecurityQuestionAttemptSelector.failed_attempts(
            user=user, hours=hours
        ).count()

    @staticmethod
    def by_ip_address(*, ip_address: str, hours: int = 24) -> QuerySet[SecurityQuestionAttempt]:
        """
        Get security question attempts by IP address.

        Args:
            ip_address: IP address
            hours: Number of hours to look back

        Returns:
            QuerySet of attempts from the IP
        """
        since = timezone.now() - timedelta(hours=hours)
        return SecurityQuestionAttempt.objects.filter(
            ip_address=ip_address,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def get_attempt_stats(*, user: CustomUser, days: int = 30) -> dict:
        """
        Get security question attempt statistics for a user.

        Args:
            user: User instance
            days: Number of days to analyze

        Returns:
            Dictionary with attempt statistics
        """
        since = timezone.now() - timedelta(days=days)
        attempts = SecurityQuestionAttempt.objects.filter(
            user=user,
            created_at__gte=since
        )
        
        total_attempts = attempts.count()
        successful_attempts = attempts.filter(success=True).count()
        
        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "failed_attempts": total_attempts - successful_attempts,
            "success_rate": round((successful_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1),
            "last_attempt": attempts.order_by('-created_at').first(),
            "last_success": attempts.filter(success=True).order_by('-created_at').first()
        }