"""
School model for Guinea's education system.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from domain.shared.models.base import AuditModel
from domain.geography.models import Locality
from ..constants import SchoolType, SchoolStatus, SchoolOwnership
from ..validators import (
    validate_school_code,
    validate_guinea_phone,
    validate_school_capacity,
    validate_school_settings,
)

User = get_user_model()


class SchoolManager(models.Manager):
    """Custom manager for School model."""
    
    def active(self):
        """Return active schools."""
        return self.filter(status=SchoolStatus.ACTIVE, is_deleted=False)
    
    def by_locality(self, locality):
        """Return schools in a specific locality."""
        return self.filter(locality=locality, is_deleted=False)
    
    def by_region(self, region):
        """Return schools in a specific region."""
        return self.filter(
            locality__administrative_unit__region=region,
            is_deleted=False
        )
    
    def by_type(self, school_type):
        """Return schools of a specific type."""
        return self.filter(school_type=school_type, is_deleted=False)
    
    def with_capacity(self, min_capacity=None, max_capacity=None):
        """Return schools within capacity range."""
        queryset = self.filter(is_deleted=False)
        
        if min_capacity is not None:
            queryset = queryset.filter(capacity__gte=min_capacity)
        if max_capacity is not None:
            queryset = queryset.filter(capacity__lte=max_capacity)
            
        return queryset
    
    def public_schools(self):
        """Return public schools."""
        return self.filter(ownership=SchoolOwnership.PUBLIC, is_deleted=False)
    
    def private_schools(self):
        """Return private schools."""
        return self.filter(ownership=SchoolOwnership.PRIVATE, is_deleted=False)


class School(AuditModel):
    """
    School model for Guinea's education system.
    
    Represents an educational institution in Guinea with proper geographic
    integration and Guinea-specific business rules.
    
    Attributes:
        name: School name (e.g., "Lycée Filima")
        code: Unique school code (e.g., "LYC-FILIMA-001")
        school_type: Type of school (primaire, collège, lycée, etc.)
        ownership: Ownership type (public, private, community, etc.)
        status: Operational status (draft, active, suspended, closed)
        locality: Geographic location (required)
        capacity: Maximum student capacity
        settings: JSON field for school-specific configuration
        director: Optional school director
        registrar: Optional registrar/admin staff
    """
    
    # Identity and Classification
    name = models.CharField(
        _('nom'),
        max_length=200,
        help_text=_('Nom complet de l\'école (ex: Lycée Filima)')
    )
    
    code = models.CharField(
        _('code'),
        max_length=50,
        unique=True,
        validators=[validate_school_code],
        help_text=_('Code unique de l\'école (ex: LYC-FILIMA-001)')
    )
    
    school_type = models.CharField(
        _('type d\'école'),
        max_length=20,
        choices=SchoolType.choices,
        help_text=_('Type d\'établissement scolaire')
    )
    
    ownership = models.CharField(
        _('statut'),
        max_length=20,
        choices=SchoolOwnership.choices,
        default=SchoolOwnership.PUBLIC,
        help_text=_('Type de propriété de l\'école')
    )
    
    status = models.CharField(
        _('état'),
        max_length=20,
        choices=SchoolStatus.choices,
        default=SchoolStatus.DRAFT,
        db_index=True,
        help_text=_('État opérationnel de l\'école')
    )
    
    # Geographic Relationship (Required)
    locality = models.ForeignKey(
        Locality,
        on_delete=models.PROTECT,
        related_name='schools',
        verbose_name=_('localité'),
        help_text=_('Localité où se situe l\'école')
    )
    
    # Contact Information
    address = models.TextField(
        _('adresse'),
        blank=True,
        help_text=_('Adresse détaillée de l\'école')
    )
    
    phone = models.CharField(
        _('téléphone'),
        max_length=20,
        blank=True,
        validators=[validate_guinea_phone],
        help_text=_('Numéro de téléphone (format Guinée)')
    )
    
    email = models.EmailField(
        _('email'),
        blank=True,
        help_text=_('Adresse email de contact')
    )
    
    website = models.URLField(
        _('site web'),
        blank=True,
        help_text=_('Site web de l\'école (optionnel)')
    )
    
    # Operational Information
    capacity = models.PositiveIntegerField(
        _('capacité'),
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Capacité maximale d\'élèves')
    )
    
    settings = models.JSONField(
        _('paramètres'),
        default=dict,
        blank=True,
        validators=[validate_school_settings],
        help_text=_('Configuration spécifique à l\'école (JSON)')
    )
    
    # Staff Relationships (Optional)
    director = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_schools',
        verbose_name=_('directeur'),
        help_text=_('Directeur de l\'école (optionnel)')
    )
    
    registrar = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administered_schools',
        verbose_name=_('registraire'),
        help_text=_('Responsable administratif (optionnel)')
    )
    
    # Custom manager
    objects = SchoolManager()
    
    class Meta:
        verbose_name = _('école')
        verbose_name_plural = _('écoles')
        ordering = ['name']
        
        indexes = [
            models.Index(fields=['code'], name='school_code_idx'),
            models.Index(fields=['status'], name='school_status_idx'),
            models.Index(fields=['school_type'], name='school_type_idx'),
            models.Index(fields=['locality'], name='school_locality_idx'),
            models.Index(fields=['locality', 'status'], name='school_locality_status_idx'),
            models.Index(fields=['capacity'], name='school_capacity_idx'),
        ]
        
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name='positive_capacity'
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.get_school_type_display()})"
    
    def clean(self):
        """Validate model data."""
        super().clean()
        
        # Validate capacity for school type
        if self.capacity and self.school_type:
            validate_school_capacity(self.capacity, self.school_type)
        
        # Business rule: Only active schools can have director/registrar
        if self.status != SchoolStatus.ACTIVE:
            if self.director or self.registrar:
                raise ValidationError(
                    _('Seules les écoles actives peuvent avoir un directeur ou registraire.')
                )
        
        # Validate locality is not deleted
        if self.locality and self.locality.is_deleted:
            raise ValidationError(
                _('Impossible d\'associer une école à une localité supprimée.')
            )
    
    def save(self, *args, **kwargs):
        """Save with validation."""
        # Auto-generate code if not provided
        if not self.code and self.school_type and self.locality:
            self.code = self._generate_school_code()
        
        super().save(*args, **kwargs)
    
    def _generate_school_code(self) -> str:
        """
        Generate a school code based on type and locality.
        
        Format: TYPE-LOCALITY-001
        """
        # Type prefix mapping
        type_prefixes = {
            SchoolType.PRESCOLAIRE: 'PRESC',
            SchoolType.PRIMAIRE: 'PRIM',
            SchoolType.COLLEGE: 'COLL',
            SchoolType.LYCEE: 'LYC',
            SchoolType.TECHNIQUE: 'TECH',
            SchoolType.SUPERIEUR: 'SUP',
            SchoolType.FORMATION_PROF: 'PROF',
        }
        
        type_prefix = type_prefixes.get(self.school_type, 'ECO')
        locality_code = self.locality.code.upper()
        
        # Find next number for this locality and type
        similar_schools = School.objects.filter(
            code__startswith=f"{type_prefix}-{locality_code}-",
            is_deleted=False
        ).count()
        
        number = str(similar_schools + 1).zfill(3)
        
        return f"{type_prefix}-{locality_code}-{number}"
    
    # Status Management Methods
    def activate(self, user=None):
        """Activate the school."""
        if self.status == SchoolStatus.DRAFT:
            self.status = SchoolStatus.ACTIVE
            self.save_by(user=user)
        else:
            raise ValidationError(
                _('Seules les écoles en brouillon peuvent être activées.')
            )
    
    def suspend(self, user=None):
        """Suspend the school."""
        if self.status == SchoolStatus.ACTIVE:
            self.status = SchoolStatus.SUSPENDED
            self.save_by(user=user)
        else:
            raise ValidationError(
                _('Seules les écoles actives peuvent être suspendues.')
            )
    
    def reactivate(self, user=None):
        """Reactivate a suspended school."""
        if self.status == SchoolStatus.SUSPENDED:
            self.status = SchoolStatus.ACTIVE
            self.save_by(user=user)
        else:
            raise ValidationError(
                _('Seules les écoles suspendues peuvent être réactivées.')
            )
    
    def close(self, user=None):
        """Close the school permanently."""
        if self.status in [SchoolStatus.ACTIVE, SchoolStatus.SUSPENDED]:
            self.status = SchoolStatus.CLOSED
            self.director = None
            self.registrar = None
            self.save_by(user=user)
        else:
            raise ValidationError(
                _('Seules les écoles actives ou suspendues peuvent être fermées.')
            )
    
    # Property Methods
    @property
    def geographic_path(self) -> str:
        """Return full geographic path."""
        return self.locality.full_path
    
    @property
    def is_operational(self) -> bool:
        """Check if school is operational."""
        return self.status == SchoolStatus.ACTIVE
    
    @property
    def has_staff(self) -> bool:
        """Check if school has assigned staff."""
        return bool(self.director or self.registrar)
    
    @property
    def default_settings(self) -> dict:
        """Return default settings for this school type."""
        from ..constants import GUINEA_SCHOOL_SETTINGS
        
        base_settings = {
            'languages': {
                'instruction_language': GUINEA_SCHOOL_SETTINGS['languages']['default_language'],
                'local_languages': []
            },
            'academic': {
                'grading_scale': GUINEA_SCHOOL_SETTINGS['academic']['default_grading_scale'],
                'academic_year_start_month': 10,  # October in Guinea
            },
            'operations': {
                'lunch_program': False,
                'transportation': False,
                'boarding': False,
            }
        }
        
        return base_settings
    
    def get_setting(self, key, default=None):
        """Get a specific setting value."""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def update_setting(self, key, value, user=None):
        """Update a specific setting."""
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
        validate_school_settings(settings_copy)
        self.settings = settings_copy
        self.save_by(user=user)