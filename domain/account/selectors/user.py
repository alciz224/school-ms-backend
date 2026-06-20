"""
User selectors.
"""

from django.db.models import QuerySet, Q, Count
from django.utils import timezone
from datetime import timedelta
from typing import Optional, List

from domain.account.models import CustomUser
from domain.account.constants import UserRole


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


class UserRoleSelector:
    """Selector for determining user roles based on relationships."""

    @staticmethod
    def get_available_roles(user: CustomUser) -> List[str]:
        """
        Détermine les rôles disponibles pour l'utilisateur, basés sur ses profils
        et ses relations.

        Logique :
        - student     : a un StudentProfile (OneToOne) actif
        - teacher     : a un TeacherProfile actif
        - parent      : a un ParentProfile actif (ou ParentChild en tant que parent)
        - admin       : a un AdminProfile actif
        - school_admin: a un SchoolAdminProfile actif (ou is_staff=True comme fallback)
        - super_admin : a un SuperAdminProfile OU is_superuser=True

        Args:
            user: instance CustomUser

        Returns:
            Liste des rôles disponibles
        """
        roles = []

        # student : profil élève actif
        student_profile = getattr(user, "student_profile", None)
        if student_profile and not student_profile.is_deleted:
            roles.append(UserRole.STUDENT)

        # teacher : profil enseignant actif
        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile and not teacher_profile.is_deleted:
            roles.append(UserRole.TEACHER)

        # parent : profil parent actif OU relations parent-enfant existantes
        parent_profile = getattr(user, "parent_profile", None)
        if parent_profile and not parent_profile.is_deleted:
            roles.append(UserRole.PARENT)

        # admin (plateforme)
        admin_profile = getattr(user, "admin_profile", None)
        if admin_profile and not admin_profile.is_deleted:
            roles.append(UserRole.ADMIN)

        # school_admin (école) — profil ou fallback is_staff
        school_admin_profile = getattr(user, "school_admin_profile", None)
        if school_admin_profile and not school_admin_profile.is_deleted:
            roles.append(UserRole.SCHOOL_ADMIN)
        elif user.is_staff and not user.is_superuser:
            roles.append(UserRole.SCHOOL_ADMIN)

        # super_admin — profil ou superuser Django
        super_admin_profile = getattr(user, "super_admin_profile", None)
        has_super_profile = super_admin_profile and not super_admin_profile.is_deleted
        if has_super_profile or user.is_superuser:
            roles.append(UserRole.SUPER_ADMIN)

        return roles

    @staticmethod
    def get_default_role(user: CustomUser) -> Optional[str]:
        """
        Get the default role for a user (first available in priority order).

        Priority order: student > teacher > parent > admin > school_admin > super_admin

        Args:
            user: User instance

        Returns:
            Default role string or None if no roles available
        """
        available = UserRoleSelector.get_available_roles(user)

        if not available:
            return None

        # Priority order
        priority = [
            UserRole.STUDENT,
            UserRole.TEACHER,
            UserRole.PARENT,
            UserRole.ADMIN,
            UserRole.SCHOOL_ADMIN,
            UserRole.SUPER_ADMIN,
        ]

        for role in priority:
            if role in available:
                return role

        # Fallback: return first available (should not reach here)
        return available[0]