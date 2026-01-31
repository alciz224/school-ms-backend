"""
School service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from domain.school_operations.models import School
from domain.school_operations.constants import SchoolStatus, SchoolType
from domain.geography.models import Locality


class SchoolService:
    """Service for school operations."""

    @staticmethod
    def create(*, name: str, school_type: str, locality: Locality,
               code: str = None, ownership: str = None, status: str = SchoolStatus.DRAFT,
               address: str = '', phone: str = '', email: str = '', website: str = '',
               capacity: int = None, settings: dict = None,
               director=None, registrar=None, user=None) -> School:
        """
        Create a new school.

        Args:
            name: School name (e.g., "Lycée Filima")
            school_type: Type of school (from SchoolType constants)
            locality: Locality where school is located
            code: Custom school code (auto-generated if not provided)
            ownership: Ownership type (defaults to PUBLIC)
            status: School status (defaults to DRAFT)
            address: School address
            phone: Contact phone number (Guinea format)
            email: Contact email
            website: School website URL
            capacity: Maximum student capacity
            settings: School-specific settings (JSON)
            director: School director user
            registrar: Registrar/admin user
            user: User performing the action

        Returns:
            Created School instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate locality is not deleted
        if locality.is_deleted:
            raise ValidationError(
                _('Impossible de créer une école dans une localité supprimée.')
            )

        # Initialize settings with Guinea defaults if not provided
        if settings is None:
            settings = {}

        school = School(
            name=name,
            code=code,
            school_type=school_type,
            ownership=ownership,
            status=status,
            locality=locality,
            address=address,
            phone=phone,
            email=email,
            website=website,
            capacity=capacity,
            settings=settings,
            director=director,
            registrar=registrar,
            created_by=user
        )

        # save() will handle code generation and validation
        school.save()
        return school

    @staticmethod
    def update(*, school: School, name: str = None, school_type: str = None,
               locality: Locality = None, code: str = None, ownership: str = None,
               address: str = None, phone: str = None, email: str = None,
               website: str = None, capacity: int = None,
               director=None, registrar=None, user=None) -> School:
        """
        Update school details.

        Args:
            school: School instance to update
            name: New school name (optional)
            school_type: New school type (optional)
            locality: New locality (optional)
            code: New school code (optional)
            ownership: New ownership type (optional)
            address: New address (optional)
            phone: New phone number (optional)
            email: New email (optional)
            website: New website (optional)
            capacity: New capacity (optional)
            director: New director (optional)
            registrar: New registrar (optional)
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If validation fails
        """
        if name is not None:
            school.name = name
        if school_type is not None:
            school.school_type = school_type
        if locality is not None:
            if locality.is_deleted:
                raise ValidationError(
                    _('Impossible d\'associer une école à une localité supprimée.')
                )
            school.locality = locality
        if code is not None:
            school.code = code
        if ownership is not None:
            school.ownership = ownership
        if address is not None:
            school.address = address
        if phone is not None:
            school.phone = phone
        if email is not None:
            school.email = email
        if website is not None:
            school.website = website
        if capacity is not None:
            school.capacity = capacity
        if director is not None:
            school.director = director
        if registrar is not None:
            school.registrar = registrar

        school.updated_by = user
        school.save()
        return school

    @staticmethod
    def activate(*, school: School, user=None) -> School:
        """
        Activate a draft school.

        Args:
            school: School instance to activate
            user: User performing the action

        Returns:
            Activated School instance

        Raises:
            ValidationError: If school cannot be activated
        """
        if school.status != SchoolStatus.DRAFT:
            raise ValidationError(
                _('Seules les écoles en brouillon peuvent être activées.')
            )

        school.status = SchoolStatus.ACTIVE
        school.updated_by = user
        school.save(update_fields=["status", "updated_at", "updated_by"])
        return school

    @staticmethod
    def suspend(*, school: School, user=None) -> School:
        """
        Suspend an active school.

        Args:
            school: School instance to suspend
            user: User performing the action

        Returns:
            Suspended School instance

        Raises:
            ValidationError: If school cannot be suspended
        """
        if school.status != SchoolStatus.ACTIVE:
            raise ValidationError(
                _('Seules les écoles actives peuvent être suspendues.')
            )

        school.status = SchoolStatus.SUSPENDED
        school.updated_by = user
        school.save(update_fields=["status", "updated_at", "updated_by"])
        return school

    @staticmethod
    def reactivate(*, school: School, user=None) -> School:
        """
        Reactivate a suspended school.

        Args:
            school: School instance to reactivate
            user: User performing the action

        Returns:
            Reactivated School instance

        Raises:
            ValidationError: If school cannot be reactivated
        """
        if school.status != SchoolStatus.SUSPENDED:
            raise ValidationError(
                _('Seules les écoles suspendues peuvent être réactivées.')
            )

        school.status = SchoolStatus.ACTIVE
        school.updated_by = user
        school.save(update_fields=["status", "updated_at", "updated_by"])
        return school

    @staticmethod
    @transaction.atomic
    def close(*, school: School, user=None) -> School:
        """
        Close a school permanently.

        Args:
            school: School instance to close
            user: User performing the action

        Returns:
            Closed School instance

        Raises:
            ValidationError: If school cannot be closed
        """
        if school.status not in [SchoolStatus.ACTIVE, SchoolStatus.SUSPENDED]:
            raise ValidationError(
                _('Seules les écoles actives ou suspendues peuvent être fermées.')
            )

        school.status = SchoolStatus.CLOSED
        school.director = None
        school.registrar = None
        school.updated_by = user
        school.save(update_fields=["status", "director", "registrar", "updated_at", "updated_by"])
        return school

    @staticmethod
    def assign_director(*, school: School, director, user=None) -> School:
        """
        Assign a director to the school.

        Args:
            school: School instance
            director: User to assign as director
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If school is not active
        """
        if school.status != SchoolStatus.ACTIVE:
            raise ValidationError(
                _('Seules les écoles actives peuvent avoir un directeur.')
            )

        school.director = director
        school.updated_by = user
        school.save(update_fields=["director", "updated_at", "updated_by"])
        return school

    @staticmethod
    def assign_registrar(*, school: School, registrar, user=None) -> School:
        """
        Assign a registrar to the school.

        Args:
            school: School instance
            registrar: User to assign as registrar
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If school is not active
        """
        if school.status != SchoolStatus.ACTIVE:
            raise ValidationError(
                _('Seules les écoles actives peuvent avoir un registraire.')
            )

        school.registrar = registrar
        school.updated_by = user
        school.save(update_fields=["registrar", "updated_at", "updated_by"])
        return school

    @staticmethod
    def update_setting(*, school: School, key: str, value, user=None) -> School:
        """
        Update a specific school setting.

        Args:
            school: School instance
            key: Setting key (supports dot notation, e.g., "academic.grading_scale")
            value: Setting value
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If setting validation fails
        """
        school.update_setting(key, value, user=user)
        return school

    @staticmethod
    def update_settings(*, school: School, settings: dict, merge: bool = True,
                       user=None) -> School:
        """
        Update multiple school settings.

        Args:
            school: School instance
            settings: Dictionary of settings to update
            merge: If True, merge with existing settings; if False, replace
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If settings validation fails
        """
        if merge:
            # Merge with existing settings
            from copy import deepcopy
            merged_settings = deepcopy(school.settings)
            
            def deep_merge(base, update):
                """Recursively merge dictionaries."""
                for key, value in update.items():
                    if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
            
            deep_merge(merged_settings, settings)
            school.settings = merged_settings
        else:
            # Replace settings entirely
            school.settings = settings

        school.updated_by = user
        school.save()
        return school

    @staticmethod
    def reset_settings(*, school: School, user=None) -> School:
        """
        Reset school settings to Guinea defaults.

        Args:
            school: School instance
            user: User performing the action

        Returns:
            Updated School instance
        """
        school.settings = school.default_settings
        school.updated_by = user
        school.save(update_fields=["settings", "updated_at", "updated_by"])
        return school

    @staticmethod
    def update_capacity(*, school: School, capacity: int, user=None) -> School:
        """
        Update school capacity with validation.

        Args:
            school: School instance
            capacity: New capacity value
            user: User performing the action

        Returns:
            Updated School instance

        Raises:
            ValidationError: If capacity is invalid for school type
        """
        from domain.school_operations.validators import validate_school_capacity
        
        # Validate capacity for school type
        validate_school_capacity(capacity, school.school_type)

        school.capacity = capacity
        school.updated_by = user
        school.save(update_fields=["capacity", "updated_at", "updated_by"])
        return school

    @staticmethod
    def regenerate_code(*, school: School, user=None) -> School:
        """
        Regenerate school code based on current type and locality.

        Args:
            school: School instance
            user: User performing the action

        Returns:
            Updated School instance
        """
        new_code = school._generate_school_code()
        school.code = new_code
        school.updated_by = user
        school.save(update_fields=["code", "updated_at", "updated_by"])
        return school

    @staticmethod
    def delete(*, school: School, user=None, hard: bool = False) -> None:
        """
        Delete a school (soft delete by default).

        Args:
            school: School instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If school has dependencies
        """
        # TODO: Add dependency checks when SchoolYear and enrollment models exist
        # Check for school years, students, teachers, etc.

        if hard:
            school.hard_delete()
        else:
            school.deleted_by = user
            school.delete()  # Uses soft delete

    @staticmethod
    def restore(*, school: School, user=None) -> School:
        """
        Restore a soft-deleted school.

        Args:
            school: School instance to restore
            user: User performing the action

        Returns:
            Restored School instance

        Raises:
            ValidationError: If locality is deleted
        """
        # Validate locality is still available
        if school.locality.is_deleted:
            raise ValidationError(
                _('Impossible de restaurer une école dont la localité est supprimée.')
            )

        school.is_deleted = False
        school.deleted_at = None
        school.deleted_by = None
        school.updated_by = user
        school.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        
        return school
