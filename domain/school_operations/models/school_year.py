"""
SchoolYear model for Guinea's education system.

This model bridges School and AcademicYear to manage school-specific
academic year operations including enrollments, capacity, and settings.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.school_operations.constants import (
    SchoolYearStatus,
    GUINEA_ACADEMIC_CALENDAR,
)
from domain.school_operations.validators import (
    validate_school_year_dates,
    validate_enrollment_period,
    validate_school_year_capacity,
    validate_school_year_settings,
)
from domain.shared.models.base import AuditModel
from domain.shared.models.managers import BaseManager


class SchoolYearManager(BaseManager):
    """Custom manager for SchoolYear model."""

    def get_active_for_school(self, school):
        """Get active school year for a specific school."""
        return self.filter(
            school=school,
            status=SchoolYearStatus.ACTIVE
        ).first()

    def get_current_for_school(self, school):
        """Get current school year for a specific school."""
        return self.filter(
            school=school,
            is_current=True
        ).first()

    def get_by_academic_year(self, academic_year):
        """Get all school years for a specific academic year."""
        return self.filter(academic_year=academic_year)

    def get_planning(self):
        """Get all school years in planning status."""
        return self.filter(status=SchoolYearStatus.PLANNING)

    def get_active(self):
        """Get all active school years."""
        return self.filter(status=SchoolYearStatus.ACTIVE)


class SchoolYear(AuditModel):
    """
    Represents a school-specific academic year for Guinea's education system.
    
    This model bridges School and AcademicYear, managing school-specific
    operations like enrollments, capacity, and year-specific settings.
    
    Business Rules:
        - Only one school year per school can have is_current = True
        - Only one school year per school can have status = ACTIVE
        - Each school can have only one SchoolYear per AcademicYear
        - start_date must be before end_date
        - enrollment_end must be before or equal to start_date
        - capacity cannot exceed school's total capacity
        - Status workflow: PLANNING → ACTIVE → COMPLETED → ARCHIVED
        - ARCHIVED years cannot be modified or set as current
        - Cannot be physically deleted if enrollments exist
        - Guinea-specific: Default start month is October
    
    Settings Structure:
        {
            'grading_periods': {
                'use_trimesters': True,
                'use_semesters': False,
                'custom_periods': []
            },
            'holidays': [
                {
                    'name': 'Christmas Break',
                    'start_date': '2024-12-20',
                    'end_date': '2025-01-05'
                }
            ],
            'attendance': {
                'minimum_attendance_percentage': 75,
                'track_tardiness': True
            },
            'assessment': {
                'grading_scale': '20_point',
                'passing_grade': 10,
                'allow_makeup_exams': True
            },
            'calendar': {
                'class_days_per_week': 5,
                'periods_per_day': 6
            },
            'policies': {
                'allow_late_enrollment': False,
                'late_enrollment_deadline': '2024-11-15',
                'transfer_deadline': '2025-03-01'
            }
        }
    """

    # Core relationships
    school = models.ForeignKey(
        'school_operations.School',
        on_delete=models.PROTECT,
        related_name='school_years',
        verbose_name=_('école'),
        help_text=_('École associée à cette année scolaire')
    )
    
    academic_year = models.ForeignKey(
        'academic.AcademicYear',
        on_delete=models.PROTECT,
        related_name='school_years',
        verbose_name=_('année académique'),
        help_text=_('Référence d\'année académique globale')
    )

    # Identification
    name = models.CharField(
        max_length=200,
        verbose_name=_('nom'),
        help_text=_('Nom lisible (ex: Lycée Filima 2024-2025)')
    )
    
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('code'),
        help_text=_('Code court auto-généré (ex: LYC-FILIMA-001-2024-2025)')
    )

    # Dates
    start_date = models.DateField(
        verbose_name=_('date de début'),
        help_text=_('Date de début de l\'année scolaire (typiquement en octobre en Guinée)')
    )
    
    end_date = models.DateField(
        verbose_name=_('date de fin'),
        help_text=_('Date de fin de l\'année scolaire (typiquement en juin)')
    )

    # Enrollment period
    enrollment_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('début des inscriptions'),
        help_text=_('Date de début de la période d\'inscription')
    )
    
    enrollment_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('fin des inscriptions'),
        help_text=_('Date de fin de la période d\'inscription')
    )

    # Capacity management
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('capacité'),
        help_text=_('Capacité totale pour cette année scolaire (ne peut pas dépasser la capacité de l\'école)')
    )
    
    current_enrollment_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('nombre d\'inscriptions actuelles'),
        help_text=_('Nombre d\'élèves actuellement inscrits (mis à jour automatiquement)')
    )

    # Status and state
    status = models.CharField(
        max_length=20,
        choices=SchoolYearStatus.choices,
        default=SchoolYearStatus.PLANNING,
        verbose_name=_('statut'),
        help_text=_('Statut de l\'année scolaire'),
        db_index=True
    )
    
    is_current = models.BooleanField(
        default=False,
        verbose_name=_('année en cours'),
        help_text=_('Indique si c\'est l\'année scolaire actuelle pour cette école')
    )

    # School year specific settings
    settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('paramètres'),
        help_text=_('Configuration spécifique à cette année scolaire (périodes, vacances, règles)')
    )

    # Notes and metadata
    description = models.TextField(
        blank=True,
        verbose_name=_('description'),
        help_text=_('Description ou notes pour cette année scolaire')
    )

    # Custom manager
    objects = SchoolYearManager()

    class Meta:
        db_table = 'school_year'
        verbose_name = _('Année Scolaire')
        verbose_name_plural = _('Années Scolaires')
        ordering = ['-start_date', 'school__name']
        
        indexes = [
            models.Index(fields=['school', 'status'], name='school_year_school_status_idx'),
            models.Index(fields=['school', 'is_current'], name='school_year_school_current_idx'),
            models.Index(fields=['academic_year'], name='school_year_academic_year_idx'),
            models.Index(fields=['status'], name='school_year_status_idx'),
            models.Index(fields=['start_date', 'end_date'], name='school_year_period_idx'),
            models.Index(fields=['school', 'start_date'], name='school_year_school_start_idx'),
        ]
        
        constraints = [
            # Unique school + academic year combination
            models.UniqueConstraint(
                fields=['school', 'academic_year'],
                condition=models.Q(is_deleted=False),
                name='unique_school_academic_year'
            ),
            # Unique school + name
            models.UniqueConstraint(
                fields=['school', 'name'],
                condition=models.Q(is_deleted=False),
                name='unique_school_year_name'
            ),
            # Unique school + date range (prevent overlapping years)
            models.UniqueConstraint(
                fields=['school', 'start_date', 'end_date'],
                condition=models.Q(is_deleted=False),
                name='unique_school_year_dates'
            ),
            # Only one current year per school
            models.UniqueConstraint(
                fields=['school'],
                condition=models.Q(is_current=True, is_deleted=False),
                name='unique_current_school_year'
            ),
            # Only one active year per school
            models.UniqueConstraint(
                fields=['school'],
                condition=models.Q(status=SchoolYearStatus.ACTIVE, is_deleted=False),
                name='unique_active_school_year'
            ),
            # Positive capacity
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0) | models.Q(capacity__isnull=True),
                name='school_year_positive_capacity'
            ),
            # Non-negative enrollment count
            models.CheckConstraint(
                condition=models.Q(current_enrollment_count__gte=0),
                name='school_year_non_negative_enrollment'
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate model fields."""
        super().clean()

        # Validate date range
        if self.start_date and self.end_date:
            validate_school_year_dates(self.start_date, self.end_date)

        # Validate enrollment period
        if self.enrollment_start_date and self.enrollment_end_date:
            validate_enrollment_period(
                self.enrollment_start_date,
                self.enrollment_end_date,
                self.start_date
            )

        # Validate capacity against school capacity
        if self.capacity and self.school_id:
            validate_school_year_capacity(self.capacity, self.school)

        # Validate settings structure
        if self.settings:
            validate_school_year_settings(self.settings)

        # Auto-generate code if not provided
        if not self.code and self.school_id and self.academic_year_id:
            self.code = self._generate_code()

        # Validate name format
        if self.name and self.school_id and self.academic_year_id:
            expected_name = self._generate_name()
            if self.name != expected_name:
                # Allow custom names, but warn
                pass

        # Only one current year per school
        if self.is_current and self.school_id:
            existing_current = (
                SchoolYear.objects.filter(
                    school=self.school,
                    is_current=True
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_current:
                raise ValidationError(
                    {'is_current': _('Une seule année scolaire peut être actuelle par école.')}
                )

        # Only one active year per school
        if self.status == SchoolYearStatus.ACTIVE and self.school_id:
            existing_active = (
                SchoolYear.objects.filter(
                    school=self.school,
                    status=SchoolYearStatus.ACTIVE
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_active:
                raise ValidationError(
                    {'status': _('Une seule année scolaire peut être active par école.')}
                )

        # ARCHIVED years cannot be current or active
        if self.status == SchoolYearStatus.ARCHIVED:
            if self.is_current:
                raise ValidationError(
                    {'is_current': _('Les années archivées ne peuvent pas être actuelles.')}
                )

        # Current year must be active
        if self.is_current and self.status != SchoolYearStatus.ACTIVE:
            raise ValidationError(
                {'is_current': _('Seules les années actives peuvent être marquées comme actuelles.')}
            )

        # Validate enrollment count doesn't exceed capacity
        if self.capacity and self.current_enrollment_count > self.capacity:
            raise ValidationError(
                {'current_enrollment_count': _(
                    f'Le nombre d\'inscriptions ({self.current_enrollment_count}) '
                    f'ne peut pas dépasser la capacité ({self.capacity}).'
                )}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        # If setting as current, unset others for this school
        if self.is_current and self.school_id:
            SchoolYear.objects.filter(
                school=self.school,
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)

        # If setting as active, unset others for this school
        if self.status == SchoolYearStatus.ACTIVE and self.school_id:
            SchoolYear.objects.filter(
                school=self.school,
                status=SchoolYearStatus.ACTIVE
            ).exclude(pk=self.pk).update(status=SchoolYearStatus.PLANNING)

        self.full_clean()
        super().save(*args, **kwargs)

    def _generate_code(self) -> str:
        """Generate school year code."""
        if not self.school or not self.academic_year:
            return ''
        
        # Format: SCHOOL_CODE-ACADEMIC_YEAR_CODE
        # Example: LYC-FILIMA-001-2024-2025
        return f"{self.school.code}-{self.academic_year.code}"

    def _generate_name(self) -> str:
        """Generate school year name."""
        if not self.school or not self.academic_year:
            return ''
        
        # Format: School Name Academic Year
        # Example: Lycée Filima 2024-2025
        return f"{self.school.name} {self.academic_year.code}"

    def get_default_settings(self) -> dict:
        """
        Get default settings for Guinea's school year.
        
        Returns:
            dict: Default settings structure
        """
        return {
            'grading_periods': {
                'use_trimesters': True,
                'use_semesters': False,
                'custom_periods': []
            },
            'holidays': [],
            'attendance': {
                'minimum_attendance_percentage': 75,
                'track_tardiness': True,
                'track_absences': True
            },
            'assessment': {
                'grading_scale': '20_point',
                'passing_grade': 10.0,
                'allow_makeup_exams': True,
                'continuous_assessment_weight': 40,
                'final_exam_weight': 60
            },
            'calendar': {
                'class_days_per_week': 5,
                'periods_per_day': 6,
                'period_duration_minutes': 55,
                'break_duration_minutes': 15
            },
            'policies': {
                'allow_late_enrollment': False,
                'late_enrollment_deadline': None,
                'transfer_deadline': None,
                'withdrawal_deadline': None
            },
            'notifications': {
                'notify_low_attendance': True,
                'notify_failing_grades': True,
                'attendance_threshold': 80
            }
        }

    def get_setting(self, key, default=None):
        """
        Get a specific setting value.
        
        Args:
            key: Dot-notation key (e.g., 'assessment.passing_grade')
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def update_setting(self, key, value, user=None):
        """
        Update a specific setting.
        
        Args:
            key: Dot-notation key (e.g., 'assessment.passing_grade')
            value: New value
            user: User making the change
        """
        keys = key.split('.')
        settings_copy = self.settings.copy()
        current = settings_copy
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set value
        current[keys[-1]] = value
        
        # Validate and save
        validate_school_year_settings(settings_copy)
        self.settings = settings_copy
        self.save_by(user=user)

    def add_holiday(self, name, start_date, end_date=None, user=None):
        """
        Add a holiday period.
        
        Args:
            name: Holiday name
            start_date: Start date
            end_date: End date (optional, defaults to start_date)
            user: User making the change
        """
        if not end_date:
            end_date = start_date
        
        holidays = self.get_setting('holidays', [])
        holidays.append({
            'name': name,
            'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date,
            'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
        })
        
        self.update_setting('holidays', holidays, user=user)

    def is_enrollment_open(self) -> bool:
        """
        Check if enrollment period is currently open.
        
        Returns:
            bool: True if enrollment is open
        """
        if not self.enrollment_start_date or not self.enrollment_end_date:
            return False
        
        from django.utils import timezone
        today = timezone.now().date()
        
        return (
            self.enrollment_start_date <= today <= self.enrollment_end_date and
            self.status in [SchoolYearStatus.PLANNING, SchoolYearStatus.ACTIVE]
        )

    def has_capacity(self) -> bool:
        """
        Check if school year has available capacity.
        
        Returns:
            bool: True if capacity available
        """
        if not self.capacity:
            return True  # No limit set
        
        return self.current_enrollment_count < self.capacity

    def available_capacity(self) -> int:
        """
        Get available capacity.
        
        Returns:
            int: Number of available spots, or None if no limit
        """
        if not self.capacity:
            return None
        
        return max(0, self.capacity - self.current_enrollment_count)

    def activate(self, user=None):
        """
        Activate this school year.
        
        Args:
            user: User performing the action
            
        Raises:
            ValidationError: If year cannot be activated
        """
        if self.status == SchoolYearStatus.ARCHIVED:
            raise ValidationError(_('Impossible d\'activer une année archivée.'))
        
        if self.status == SchoolYearStatus.ACTIVE:
            return  # Already active
        
        # Deactivate other active years for this school
        SchoolYear.objects.filter(
            school=self.school,
            status=SchoolYearStatus.ACTIVE
        ).exclude(pk=self.pk).update(
            status=SchoolYearStatus.PLANNING,
            is_current=False
        )
        
        self.status = SchoolYearStatus.ACTIVE
        self.is_current = True
        self.save_by(user=user)

    def complete(self, user=None):
        """
        Mark this school year as completed.
        
        Args:
            user: User performing the action
            
        Raises:
            ValidationError: If year cannot be completed
        """
        if self.status != SchoolYearStatus.ACTIVE:
            raise ValidationError(
                _('Seules les années actives peuvent être marquées comme terminées.')
            )
        
        self.status = SchoolYearStatus.COMPLETED
        self.is_current = False
        self.save_by(user=user)

    def archive(self, user=None):
        """
        Archive this school year.
        
        Args:
            user: User performing the action
            
        Raises:
            ValidationError: If year cannot be archived
        """
        if self.status == SchoolYearStatus.ARCHIVED:
            return  # Already archived
        
        if self.status == SchoolYearStatus.ACTIVE:
            raise ValidationError(
                _('Les années actives doivent d\'abord être marquées comme terminées.')
            )
        
        self.status = SchoolYearStatus.ARCHIVED
        self.is_current = False
        self.save_by(user=user)

    def can_be_deleted(self) -> tuple[bool, str]:
        """
        Check if school year can be deleted.
        
        Returns:
            tuple: (can_delete, reason)
        """
        # Check for enrollments (would be implemented when enrollment model exists)
        # if self.enrollments.exists():
        #     return False, _('Cannot delete school year with enrollments')
        
        # Check for classes (would be implemented when classroom model exists)
        # if self.classrooms.exists():
        #     return False, _('Cannot delete school year with classes')
        
        if self.status == SchoolYearStatus.ACTIVE:
            return False, _('Impossible de supprimer une année scolaire active.')
        
        if self.is_current:
            return False, _('Impossible de supprimer l\'année scolaire actuelle.')
        
        return True, ''

    def increment_enrollment_count(self, count=1):
        """
        Increment enrollment count.
        
        Args:
            count: Number to increment by (default: 1)
        """
        # Use update() to bypass full_clean() for F() expressions
        SchoolYear.objects.filter(pk=self.pk).update(
            current_enrollment_count=models.F('current_enrollment_count') + count
        )
        self.refresh_from_db(fields=['current_enrollment_count'])

    def decrement_enrollment_count(self, count=1):
        """
        Decrement enrollment count.
        
        Args:
            count: Number to decrement by (default: 1)
        """
        # Use update() to bypass full_clean() for F() expressions
        SchoolYear.objects.filter(pk=self.pk).update(
            current_enrollment_count=models.F('current_enrollment_count') - count
        )
        self.refresh_from_db(fields=['current_enrollment_count'])
