# Domain Model Implementation - Real Examples

**Real-world examples from existing implementations in the codebase**

This document shows actual implementations from the `academic`, `geography`, and `school_operations` domains to demonstrate how the patterns are applied in practice.

---

## Table of Contents

1. [Simple Model Example: Country (Geography)](#1-simple-model-example-country-geography)
2. [Medium Complexity: AcademicYear (Academic)](#2-medium-complexity-academicyear-academic)
3. [Complex Model: School (School Operations)](#3-complex-model-school-school-operations)
4. [Pattern Comparison Table](#4-pattern-comparison-table)

---

## 1. Simple Model Example: Country (Geography)

### Model: `domain/geography/models/country.py`

**Key Features:**
- Basic fields (code, name)
- Simple validation
- No foreign keys
- Standard AuditModel inheritance

```python
"""Country model."""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.shared.models.base import AuditModel


class Country(AuditModel):
    """
    Country model representing a sovereign nation.
    
    Business Rules:
        - Code must be unique (ISO 3166-1 alpha-2 standard)
        - Name must be unique
        - Code should be uppercase 2-letter format
    
    Attributes:
        code: Two-letter ISO country code (e.g., 'US', 'CA')
        name: Official country name
        native_name: Country name in native language (optional)
    """
    
    code = models.CharField(
        max_length=2,
        unique=True,
        db_index=True,
        help_text=_("Two-letter ISO country code (e.g., US, CA)")
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Official country name in English")
    )
    
    native_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Country name in native language (optional)")
    )
    
    class Meta:
        db_table = "country"
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"], name="country_code_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_country_code",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate country fields."""
        super().clean()
        
        # Normalize code to uppercase
        if self.code:
            self.code = self.code.upper().strip()
        
        # Validate code format
        if self.code and len(self.code) != 2:
            raise ValidationError({"code": _("Country code must be exactly 2 characters.")})
```

### Service: `domain/geography/services/country.py`

```python
"""Country service."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models import Country


class CountryService:
    """Service for country operations."""
    
    @staticmethod
    def create(*, code: str, name: str, native_name: str = None, user=None) -> Country:
        """
        Create a new country.
        
        Args:
            code: Two-letter ISO country code
            name: Country name in English
            native_name: Country name in native language (optional)
            user: User performing the action
        
        Returns:
            Created Country instance
        
        Raises:
            ValidationError: If validation fails
        """
        country = Country(
            code=code.upper().strip(),
            name=name.strip(),
            native_name=native_name.strip() if native_name else "",
            created_by=user
        )
        country.full_clean()
        country.save()
        return country
    
    @staticmethod
    def update(*, country: Country, name: str = None, native_name: str = None, 
               user=None) -> Country:
        """
        Update a country.
        
        Args:
            country: Country instance to update
            name: New name (optional)
            native_name: New native name (optional)
            user: User performing the action
        
        Returns:
            Updated Country instance
        """
        if name is not None:
            country.name = name.strip()
        
        if native_name is not None:
            country.native_name = native_name.strip()
        
        country.updated_by = user
        country.full_clean()
        country.save()
        return country
    
    @staticmethod
    def delete(*, country: Country, user=None, hard: bool = False) -> None:
        """
        Delete a country (soft delete by default).
        
        Args:
            country: Country instance to delete
            user: User performing the action
            hard: If True, permanently delete
        
        Raises:
            ValidationError: If country has dependencies
        """
        # Check for dependencies
        if country.regions.filter(is_deleted=False).exists():
            raise ValidationError(
                _("Cannot delete country with existing regions. "
                  "Delete or reassign regions first.")
            )
        
        if hard:
            country.hard_delete()
        else:
            country.deleted_by = user
            country.delete()
```

### Selector: `domain/geography/selectors/country.py`

```python
"""Country selectors."""
from django.db.models import QuerySet, Q, Count
from typing import Optional

from domain.geography.models import Country


class CountrySelector:
    """Selector for country queries."""
    
    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Country]:
        """Get all countries."""
        if include_deleted:
            return Country.all_objects.all()
        return Country.objects.all()
    
    @staticmethod
    def get_by_id(*, country_id: int, include_deleted: bool = False) -> Optional[Country]:
        """Get a country by ID."""
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(id=country_id).first()
    
    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[Country]:
        """Get a country by code."""
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(code__iexact=code.strip()).first()
    
    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[Country]:
        """Search countries by name or code."""
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) |
            Q(native_name__icontains=query)
        )
    
    @staticmethod
    def get_with_region_counts() -> QuerySet[Country]:
        """Get all countries with region counts."""
        return Country.objects.annotate(
            region_count=Count('regions', filter=Q(regions__is_deleted=False))
        )
```

**Lessons from Country:**
- Simple, clean structure
- Code normalization in `clean()` method
- Dependency checks in service delete
- Multiple search fields in selector
- Annotated queries for counts

---

## 2. Medium Complexity: AcademicYear (Academic)

### Model: `domain/academic/models/academic_year.py`

**Key Features:**
- Composite unique constraint (start_year + end_year)
- Business logic (is_current flag management)
- Date range validation
- Custom manager methods

```python
"""AcademicYear model."""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.shared.models.base import AuditModel


class AcademicYear(AuditModel):
    """
    Academic Year model representing a school year period.
    
    Business Rules:
        - Only one academic year can be current at a time
        - End year must be exactly start year + 1
        - Start year must be between 1900 and current year + 10
        - Code is auto-generated from start and end years
    
    Attributes:
        code: Auto-generated code (e.g., '2023-2024')
        start_year: Starting year of the academic year
        end_year: Ending year of the academic year
        is_current: Whether this is the current active academic year
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text=_("Auto-generated code (e.g., 2023-2024)")
    )
    
    start_year = models.IntegerField(
        help_text=_("Starting year of the academic year")
    )
    
    end_year = models.IntegerField(
        help_text=_("Ending year of the academic year")
    )
    
    is_current = models.BooleanField(
        default=False,
        help_text=_("Whether this is the current academic year")
    )
    
    class Meta:
        db_table = "academic_year"
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")
        ordering = ["-start_year"]
        indexes = [
            models.Index(fields=["start_year"], name="academic_year_start_idx"),
            models.Index(fields=["is_current"], name="academic_year_current_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["start_year", "end_year"],
                condition=models.Q(is_deleted=False),
                name="unique_academic_year_period",
            ),
            models.CheckConstraint(
                check=models.Q(end_year=models.F('start_year') + 1),
                name="academic_year_consecutive",
            ),
        ]
    
    def __str__(self) -> str:
        return self.code
    
    def clean(self):
        """Validate academic year fields."""
        super().clean()
        
        # Validate year range
        if self.start_year and self.end_year:
            if self.end_year != self.start_year + 1:
                raise ValidationError({
                    "end_year": _("End year must be exactly one year after start year.")
                })
        
        # Validate start year is reasonable
        from django.utils import timezone
        current_year = timezone.now().year
        if self.start_year and (self.start_year < 1900 or self.start_year > current_year + 10):
            raise ValidationError({
                "start_year": _("Start year must be between 1900 and %(max_year)s.") % {
                    'max_year': current_year + 10
                }
            })
    
    def save(self, *args, **kwargs):
        """Save with auto-generated code."""
        # Auto-generate code from years
        if self.start_year and self.end_year:
            self.code = f"{self.start_year}-{self.end_year}"
        
        # Validate before saving
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        
        super().save(*args, **kwargs)
    
    @property
    def display_name(self) -> str:
        """Get display name for the academic year."""
        return f"Academic Year {self.code}"
```

### Service: `domain/academic/services/academic_year.py`

```python
"""AcademicYear service."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from domain.academic.models import AcademicYear


class AcademicYearService:
    """Service for academic year operations."""
    
    @staticmethod
    def create(*, start_year: int, end_year: int, is_current: bool = False, 
               user=None) -> AcademicYear:
        """
        Create a new academic year.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            is_current: Whether this should be the current year
            user: User performing the action
        
        Returns:
            Created AcademicYear instance
        
        Raises:
            ValidationError: If validation fails
        """
        academic_year = AcademicYear(
            start_year=start_year,
            end_year=end_year,
            is_current=is_current,
            created_by=user
        )
        academic_year.save()
        
        # If setting as current, unset other current years
        if is_current:
            AcademicYearService._unset_other_current(academic_year, user)
        
        return academic_year
    
    @staticmethod
    @transaction.atomic
    def set_current(*, academic_year: AcademicYear, user=None) -> AcademicYear:
        """
        Set an academic year as current (unsets others).
        
        Args:
            academic_year: AcademicYear instance to set as current
            user: User performing the action
        
        Returns:
            Updated AcademicYear instance
        """
        # Unset all other current years
        AcademicYear.objects.filter(is_current=True).update(
            is_current=False,
            updated_by=user
        )
        
        # Set this one as current
        academic_year.is_current = True
        academic_year.updated_by = user
        academic_year.save(update_fields=['is_current', 'updated_at', 'updated_by'])
        
        return academic_year
    
    @staticmethod
    def _unset_other_current(academic_year: AcademicYear, user=None):
        """Unset is_current flag on all other academic years."""
        AcademicYear.objects.filter(is_current=True).exclude(
            id=academic_year.id
        ).update(is_current=False, updated_by=user)
    
    @staticmethod
    def delete(*, academic_year: AcademicYear, user=None, hard: bool = False) -> None:
        """
        Delete an academic year.
        
        Args:
            academic_year: AcademicYear instance to delete
            user: User performing the action
            hard: If True, permanently delete
        
        Raises:
            ValidationError: If academic year is current or has dependencies
        """
        # Prevent deletion of current academic year
        if academic_year.is_current:
            raise ValidationError(
                _("Cannot delete the current academic year. "
                  "Please set another year as current first.")
            )
        
        # Check for dependencies (terms, etc.)
        if academic_year.terms.filter(is_deleted=False).exists():
            raise ValidationError(
                _("Cannot delete academic year with existing terms. "
                  "Delete or reassign terms first.")
            )
        
        if hard:
            academic_year.hard_delete()
        else:
            academic_year.deleted_by = user
            academic_year.delete()
```

### Selector: `domain/academic/selectors/academic_year.py`

```python
"""AcademicYear selectors."""
from django.db.models import QuerySet, Count, Q
from typing import Optional

from domain.academic.models import AcademicYear


class AcademicYearSelector:
    """Selector for academic year queries."""
    
    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[AcademicYear]:
        """Get all academic years."""
        if include_deleted:
            return AcademicYear.all_objects.all()
        return AcademicYear.objects.all()
    
    @staticmethod
    def get_current() -> Optional[AcademicYear]:
        """Get the current academic year."""
        return AcademicYear.objects.filter(is_current=True).first()
    
    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[AcademicYear]:
        """Get an academic year by code."""
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(code__iexact=code.strip()).first()
    
    @staticmethod
    def get_by_year_range(*, start_year: int, end_year: int, 
                          include_deleted: bool = False) -> Optional[AcademicYear]:
        """Get an academic year by year range."""
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(
            start_year=start_year,
            end_year=end_year
        ).first()
    
    @staticmethod
    def get_with_term_counts() -> QuerySet[AcademicYear]:
        """Get all academic years with term counts."""
        return AcademicYear.objects.annotate(
            term_count=Count('terms', filter=Q(terms__is_deleted=False))
        )
```

**Lessons from AcademicYear:**
- Auto-generated code field in `save()` method
- Business rule enforcement (only one current)
- `@transaction.atomic` for operations affecting multiple records
- Custom selector method (`get_current()`)
- Prevent deletion of critical records (current year)
- Check constraint in database for data integrity

---

## 3. Complex Model: School (School Operations)

### Model: `domain/school_operations/models/school.py`

**Key Features:**
- Multiple foreign keys
- Status management with choices
- Complex validation rules
- Hierarchical data (address fields)
- Multiple related objects

```python
"""School model."""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.shared.models.base import AuditModel
from domain.school_operations.constants import SchoolStatus, SchoolType
from domain.school_operations.validators import validate_school_code


class School(AuditModel):
    """
    School model representing an educational institution.
    
    Business Rules:
        - Code must be unique and follow format rules
        - Only operational schools can have students/staff
        - Cannot delete school with active students
        - Must have valid locality reference
    
    Attributes:
        code: Unique school code
        name: Official school name
        short_name: Abbreviated name
        school_type: Type of school (public, private, etc.)
        status: Operational status
        locality: Geographic locality
        address: Physical address details
        contact: Contact information
        capacity: Maximum student capacity
    """
    
    # Identity fields
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[validate_school_code],
        help_text=_("Unique school code (alphanumeric, uppercase)")
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Official school name")
    )
    
    short_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Abbreviated school name (optional)")
    )
    
    # Classification
    school_type = models.CharField(
        max_length=20,
        choices=SchoolType.choices,
        help_text=_("Type of school")
    )
    
    status = models.CharField(
        max_length=20,
        choices=SchoolStatus.choices,
        default=SchoolStatus.OPERATIONAL,
        help_text=_("Current operational status")
    )
    
    # Geographic reference
    locality = models.ForeignKey(
        'geography.Locality',
        on_delete=models.PROTECT,
        related_name='schools',
        help_text=_("Geographic locality where school is located")
    )
    
    # Address information
    address_line1 = models.CharField(
        max_length=200,
        help_text=_("Street address line 1")
    )
    
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Street address line 2 (optional)")
    )
    
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Postal/ZIP code (optional)")
    )
    
    # Contact information
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Primary phone number (optional)")
    )
    
    email = models.EmailField(
        blank=True,
        help_text=_("Primary email address (optional)")
    )
    
    website = models.URLField(
        blank=True,
        help_text=_("School website URL (optional)")
    )
    
    # Capacity
    student_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum student capacity (optional)")
    )
    
    class Meta:
        db_table = "school"
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"], name="school_code_idx"),
            models.Index(fields=["status"], name="school_status_idx"),
            models.Index(fields=["locality"], name="school_locality_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_school_code",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate school fields."""
        super().clean()
        
        # Normalize code
        if self.code:
            self.code = self.code.upper().strip()
        
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
        
        # Validate capacity if provided
        if self.student_capacity is not None and self.student_capacity <= 0:
            raise ValidationError({
                "student_capacity": _("Student capacity must be a positive number.")
            })
    
    @property
    def is_operational(self) -> bool:
        """Check if school is operational."""
        return self.status == SchoolStatus.OPERATIONAL and not self.is_deleted
    
    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        if self.locality:
            parts.append(str(self.locality))
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts)
    
    def can_be_deleted(self) -> tuple[bool, str]:
        """
        Check if school can be deleted.
        
        Returns:
            Tuple of (can_delete, reason_if_not)
        """
        # Check for active students
        # if self.students.filter(is_deleted=False).exists():
        #     return False, "School has active students"
        
        # Check for active staff
        # if self.staff.filter(is_deleted=False).exists():
        #     return False, "School has active staff"
        
        return True, ""
```

**Lessons from School:**
- Complex model with multiple field groups
- Foreign key to another domain (geography.Locality)
- Custom validator function imported from validators.py
- Constants for choices (SchoolStatus, SchoolType)
- Property methods for computed values (`is_operational`, `full_address`)
- Business logic method (`can_be_deleted()`)
- Comprehensive address fields
- Optional fields with blank=True

---

## 4. Pattern Comparison Table

| Aspect | Country (Simple) | AcademicYear (Medium) | School (Complex) |
|--------|------------------|----------------------|------------------|
| **Fields** | 3 data fields | 4 data fields | 15+ data fields |
| **Foreign Keys** | None | None | 1 (Locality) |
| **Choices/Constants** | None | None | 2 (Status, Type) |
| **Custom Validators** | None | None | Yes (code format) |
| **Auto-generated Fields** | None | Yes (code) | None |
| **Business Rules** | Simple uniqueness | Current flag mgmt | Multiple complex rules |
| **Property Methods** | None | 1 (display_name) | 2 (is_operational, full_address) |
| **Custom Manager** | No | No | Could benefit |
| **Transaction Usage** | No | Yes (set_current) | Would need for complex ops |
| **Dependency Checks** | Yes (regions) | Yes (terms, current) | Yes (students, staff) |
| **Annotations** | Yes (region_count) | Yes (term_count) | Would add (student_count) |

---

## Key Takeaways

### When to Use Each Pattern

**Simple Pattern (Country-style):**
- Independent reference data
- Minimal business logic
- Few fields
- No complex relationships
- Examples: Country, Currency, Language

**Medium Pattern (AcademicYear-style):**
- Core business entities
- Some business logic (flags, states)
- Auto-generated fields
- Single-record rules (is_current)
- Examples: AcademicYear, Term, Cycle

**Complex Pattern (School-style):**
- Central business entities
- Multiple relationships
- Complex validation
- Hierarchical data
- Multiple states/statuses
- Examples: School, Student, Staff, Course

### Common Patterns Across All

1. **Always inherit from AuditModel**
2. **Always include proper Meta class**
3. **Always implement `__str__()`**
4. **Always use selectors for queries**
5. **Always use services for modifications**
6. **Always check dependencies before delete**
7. **Always track user actions**
8. **Always validate in `clean()` method**

---

**For implementation templates and complete patterns, see:**
- [Implementation Guide](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)
- [Quick Reference](DOMAIN_MODEL_QUICK_REFERENCE.md)
