"""
Verification code selectors.
"""

from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from domain.account.models import VerificationCode, CustomUser


class VerificationCodeSelector:
    """Selector for verification code queries."""

    @staticmethod
    def get_by_id(*, code_id: str) -> Optional[VerificationCode]:
        """
        Get a verification code by ID.

        Args:
            code_id: Code UUID

        Returns:
            VerificationCode instance or None
        """
        return VerificationCode.objects.filter(id=code_id).first()

    @staticmethod
    def for_user(*, user: CustomUser) -> QuerySet[VerificationCode]:
        """
        Get all verification codes for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of verification codes ordered by creation date
        """
        return VerificationCode.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def for_user_by_type(*, user: CustomUser, verification_type: str) -> QuerySet[VerificationCode]:
        """
        Get verification codes for a user by type.

        Args:
            user: User instance
            verification_type: Type of verification (EMAIL, PHONE, etc.)

        Returns:
            QuerySet of verification codes
        """
        return VerificationCode.objects.filter(
            user=user,
            type=verification_type
        ).order_by('-created_at')

    @staticmethod
    def get_active_code(*, user: CustomUser, verification_type: str) -> Optional[VerificationCode]:
        """
        Get the most recent active (non-verified, non-expired) code for a user.

        Args:
            user: User instance
            verification_type: Type of verification

        Returns:
            Active VerificationCode instance or None
        """
        return VerificationCode.objects.filter(
            user=user,
            type=verification_type,
            verified=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

    @staticmethod
    def get_by_code_and_user(*, user: CustomUser, code: str, 
                            verification_type: str) -> Optional[VerificationCode]:
        """
        Get a verification code by code value, user, and type.

        Args:
            user: User instance
            code: Verification code
            verification_type: Type of verification

        Returns:
            VerificationCode instance or None
        """
        return VerificationCode.objects.filter(
            user=user,
            code=code,
            type=verification_type
        ).first()

    @staticmethod
    def recent_codes(*, user: CustomUser, verification_type: str, 
                     minutes: int = 60) -> QuerySet[VerificationCode]:
        """
        Get recent verification codes for a user.

        Args:
            user: User instance
            verification_type: Type of verification
            minutes: Number of minutes to look back

        Returns:
            QuerySet of recent verification codes
        """
        since = timezone.now() - timedelta(minutes=minutes)
        return VerificationCode.objects.filter(
            user=user,
            type=verification_type,
            created_at__gte=since
        ).order_by('-created_at')

    @staticmethod
    def verified_codes(*, user: CustomUser) -> QuerySet[VerificationCode]:
        """
        Get verified codes for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of verified codes
        """
        return VerificationCode.objects.filter(
            user=user,
            verified=True
        ).order_by('-verified_at')

    @staticmethod
    def expired_codes(*, user: CustomUser) -> QuerySet[VerificationCode]:
        """
        Get expired codes for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of expired codes
        """
        return VerificationCode.objects.filter(
            user=user,
            verified=False,
            expires_at__lte=timezone.now()
        ).order_by('-created_at')

    @staticmethod
    def get_last_verified_code(*, user: CustomUser, 
                               verification_type: str) -> Optional[VerificationCode]:
        """
        Get the last successfully verified code for a user by type.

        Args:
            user: User instance
            verification_type: Type of verification

        Returns:
            Last verified VerificationCode instance or None
        """
        return VerificationCode.objects.filter(
            user=user,
            type=verification_type,
            verified=True
        ).order_by('-verified_at').first()

    @staticmethod
    def can_send_new_code(*, user: CustomUser, verification_type: str, 
                         cooldown_seconds: int = 60) -> bool:
        """
        Check if a new verification code can be sent (cooldown check).

        Args:
            user: User instance
            verification_type: Type of verification
            cooldown_seconds: Cooldown period in seconds

        Returns:
            True if new code can be sent
        """
        since = timezone.now() - timedelta(seconds=cooldown_seconds)
        recent_count = VerificationCode.objects.filter(
            user=user,
            type=verification_type,
            created_at__gte=since
        ).count()
        
        return recent_count == 0

    @staticmethod
    def get_failed_attempt_count(*, user: CustomUser, verification_type: str,
                                hours: int = 24) -> int:
        """
        Get the number of failed verification attempts.

        Args:
            user: User instance
            verification_type: Type of verification
            hours: Number of hours to look back

        Returns:
            Number of failed attempts
        """
        since = timezone.now() - timedelta(hours=hours)
        return VerificationCode.objects.filter(
            user=user,
            type=verification_type,
            verified=False,
            created_at__gte=since
        ).count()

    @staticmethod
    def get_verification_stats(*, user: CustomUser, days: int = 30) -> dict:
        """
        Get verification statistics for a user.

        Args:
            user: User instance
            days: Number of days to analyze

        Returns:
            Dictionary with verification statistics
        """
        since = timezone.now() - timedelta(days=days)
        codes = VerificationCode.objects.filter(
            user=user,
            created_at__gte=since
        )
        
        total_codes = codes.count()
        verified_codes = codes.filter(verified=True).count()
        expired_codes = codes.filter(
            verified=False,
            expires_at__lte=timezone.now()
        ).count()
        
        return {
            "total_codes_sent": total_codes,
            "verified_codes": verified_codes,
            "expired_codes": expired_codes,
            "pending_codes": total_codes - verified_codes - expired_codes,
            "verification_rate": round((verified_codes / total_codes * 100) if total_codes > 0 else 0, 1),
            "last_code": codes.order_by('-created_at').first(),
            "last_verified": codes.filter(verified=True).order_by('-verified_at').first()
        }