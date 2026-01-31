# School Model - Domain Integration Analysis

## Cross-Domain Relationships

### Integration with Geography Domain

**Dependency**: School → Locality (Required)

```python
# School model
locality = models.ForeignKey(
    'geography.Locality',
    on_delete=models.PROTECT,
    related_name='schools',
    verbose_name=_('locality')
)
```

**Benefits**:
- Automatic geographic hierarchy access (Country → Region → Unit → Locality → School)
- Query schools by any geographic level
- Preserve referential integrity

**Usage Examples**:
```python
# Get school's full geographic path
school.locality.full_path
# Output: "Guinea > Boké > Boké > Kassapo > École Primaire de Kassapo"

# Query patterns
School.objects.filter(locality__administrative_unit__region__code='BOKE')
School.objects.filter(locality__administrative_unit__type='PREFECTURE')
```

**Reverse Relationship** (from Locality):
```python
# In Locality model (no code changes needed)
# Django automatically creates: locality.schools (related_name)

locality = Locality.objects.get(code='KASSAPO')
schools_in_kassapo = locality.schools.filter(is_deleted=False)
```

### Integration with Account Domain

**Dependencies**: School → CustomUser (Optional)

```python
# School model
director = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='schools_as_director',
    verbose_name=_('director')
)

registrar = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='schools_as_registrar',
    verbose_name=_('registrar')
)
```

**Benefits**:
- Link school leadership to user accounts
- Audit trail preserved (created_by, updated_by from AuditModel)
- Users can manage schools they're assigned to
- Flexible role assignment (can be changed without data loss)

**Usage Examples**:
```python
# Assign director
school.director = user
school.save_by(user=current_user)

# Query schools by director
user.schools_as_director.all()

# Find schools without assigned director
School.objects.filter(director__isnull=True, status='ACTIVE')
```

**Reverse Relationships** (from CustomUser):
```python
# In CustomUser model (no code changes needed)
# Django automatically creates:
# - user.schools_as_director
# - user.schools_as_registrar

user = CustomUser.objects.get(email='director@example.com')
managed_schools = user.schools_as_director.filter(is_deleted=False)
```

### Integration with Academic Domain

**Future Relationship**: SchoolYear (many-to-many through table)

```python
# Future model: SchoolYear
class SchoolYear(AuditModel):
    """
    Represents a school-specific academic year.
    Links a School with an AcademicYear for operational configuration.
    """
    school = models.ForeignKey(
        'school_operations.School',
        on_delete=models.PROTECT,
        related_name='school_years'
    )
    academic_year = models.ForeignKey(
        'academic.AcademicYear',
        on_delete=models.PROTECT,
        related_name='school_years'
    )
    # School-specific configuration
    start_date = models.DateField()
    end_date = models.DateField()
    enrollment_start = models.DateField()
    enrollment_end = models.DateField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'academic_year'],
                condition=models.Q(is_deleted=False),
                name='unique_school_academic_year'
            )
        ]
```

**Relationship Pattern**:
```
AcademicYear (Global)  ←→  SchoolYear (Per School)  ←→  School
    "2024-2025"                    ↓                    "EP Kassapo"
                            - start: 2024-10-01
                            - end: 2025-06-30
                            - enrollment: 2024-08-01 to 2024-09-15
```

**Why This Design?**:
- AcademicYear remains a global reference (no school dependency)
- SchoolYear provides school-specific implementation details
- Schools can have different start dates for same academic year
- Enrollment periods can vary by school
- Clean separation of concerns

## Consistency Patterns

### Pattern 1: Code + Name Uniqueness

**Consistent Across**:
- AcademicYear: `code` (global unique)
- Subject: `code` (global unique), `name` (global unique)
- Cycle: `code` (global unique), `name` (global unique)
- Country: `code` (global unique), `name` (global unique)
- Region: `code` (per country unique), `name` (per country unique)
- Locality: `code` (per unit unique), `name` (per unit unique)

**School Implementation**:
```python
constraints = [
    models.UniqueConstraint(
        fields=["code"],
        condition=models.Q(is_deleted=False),
        name="unique_school_code"
    ),
    models.UniqueConstraint(
        fields=["locality", "name"],
        condition=models.Q(is_deleted=False),
        name="unique_school_name_per_locality"
    ),
]
```

**Rationale**:
- `code`: Global unique (like other entity codes)
- `name`: Scoped unique (realistic - "École Primaire" exists in many localities)

### Pattern 2: Status Enums

**Consistent Pattern**:
```python
# AcademicYear
class AcademicYearStatus:
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

# School (similar but domain-specific)
class SchoolStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    ACTIVE = "ACTIVE", _("Active")
    SUSPENDED = "SUSPENDED", _("Suspended")
    CLOSED = "CLOSED", _("Closed")
```

**Differences**:
- School uses `TextChoices` (newer Django pattern) vs class constants
- School has SUSPENDED and CLOSED (domain-specific needs)
- AcademicYear has ARCHIVED (time-based archival)

**Migration Path**:
- Consider migrating academic domain to TextChoices in future
- Current implementation is backward compatible

### Pattern 3: Soft Delete with Constraints

**Universal Pattern**:
```python
# All models with unique constraints
models.UniqueConstraint(
    fields=['field_name'],
    condition=models.Q(is_deleted=False),
    name='unique_constraint_name'
)
```

**Applied Consistently**:
- ✓ AcademicYear: unique code/period when not deleted
- ✓ Subject: unique code/name when not deleted
- ✓ Geography models: unique codes when not deleted
- ✓ School: unique code/name when not deleted

**Why It Matters**:
- Allows code/name reuse after deletion
- Maintains historical data integrity
- Prevents duplicate active records

### Pattern 4: Foreign Key Protection

**Pattern by Domain**:

| Domain | Model | FK Relationship | on_delete | Rationale |
|--------|-------|-----------------|-----------|-----------|
| Geography | Region | → Country | PROTECT | Cannot delete country with regions |
| Geography | Unit | → Region | PROTECT | Cannot delete region with units |
| Geography | Locality | → Unit | PROTECT | Cannot delete unit with localities |
| Academic | Term | → AcademicYear | PROTECT | Cannot delete year with terms |
| Academic | Level | → Cycle | PROTECT | Cannot delete cycle with levels |
| **School** | **School** | **→ Locality** | **PROTECT** | **Cannot delete locality with schools** |
| **School** | **School** | **→ User** | **SET_NULL** | **Can remove user, school remains** |

**School Follows Geography Pattern**:
- Reference data (Locality) uses PROTECT
- Optional relationships (director/registrar) use SET_NULL
- Critical data cannot be accidentally deleted

### Pattern 5: Audit Trail (AuditModel)

**Consistent Implementation**:

| Model | Base Class | has_created_by | has_updated_by | has_deleted_by | has_is_active |
|-------|------------|----------------|----------------|----------------|---------------|
| AcademicYear | AuditModel | ✓ | ✓ | ✓ | ✓ |
| Subject | AuditModel | ✓ | ✓ | ✓ | ✓ |
| Cycle | AuditModel | ✓ | ✓ | ✓ | ✓ |
| Country | GeographyBaseModel | ✓ | ✓ | ✓ | ✗ |
| **School** | **AuditModel** | **✓** | **✓** | **✓** | **✓** |

**School = Business Entity**:
- Uses AuditModel (not GeographyBaseModel)
- Requires activation management (is_active)
- Full audit trail (who created, updated, deleted)
- Soft delete capability

**Why Not GeographyBaseModel?**:
- Geography models are reference data (always "active")
- Schools are operational entities (can be inactive/suspended)
- Schools need activation workflow

## Query Patterns

### Pattern 1: Cross-Domain Filtering

**Geography Hierarchy Queries**:
```python
# All schools in a country
School.objects.filter(
    locality__administrative_unit__region__country=country
)

# All schools in a region
School.objects.filter(
    locality__administrative_unit__region=region
)

# All schools in a prefecture
School.objects.filter(
    locality__administrative_unit=unit,
    locality__administrative_unit__type='PREFECTURE'
)

# All schools in a locality
School.objects.filter(locality=locality)
```

**Optimization**:
- Indexes on locality FK
- select_related for efficient joins
```python
School.objects.select_related(
    'locality',
    'locality__administrative_unit',
    'locality__administrative_unit__region',
    'locality__administrative_unit__region__country'
).filter(...)
```

### Pattern 2: User-Centric Queries

**From User Perspective**:
```python
# Get user's schools as director
user.schools_as_director.filter(is_deleted=False)

# Get user's schools as registrar
user.schools_as_registrar.filter(status='ACTIVE')

# Get all schools user has created
School.objects.filter(created_by=user)

# Get all schools user manages (either role)
from django.db.models import Q
School.objects.filter(
    Q(director=user) | Q(registrar=user),
    is_deleted=False
)
```

### Pattern 3: Status-Based Queries

**Following AcademicYear Pattern**:
```python
# AcademicYear pattern
AcademicYear.objects.filter(status=AcademicYearStatus.ACTIVE)
AcademicYear.active.all()  # Using custom manager

# School pattern (consistent)
School.objects.filter(status=SchoolStatus.ACTIVE)
School.active.all()  # Using AuditModel's ActiveManager

# School-specific (operational schools)
School.objects.filter(
    status=SchoolStatus.ACTIVE,
    is_active=True,
    is_deleted=False
)
# Or using custom manager:
School.objects.active_operational()  # Custom method
```

### Pattern 4: Capacity Management

**Unique to School Domain**:
```python
# Schools at capacity
School.objects.filter(
    current_enrollment__gte=models.F('capacity'),
    capacity__isnull=False
)

# Schools with available capacity
School.objects.filter(
    current_enrollment__lt=models.F('capacity'),
    capacity__isnull=False
)

# Schools with 90%+ capacity
School.objects.filter(
    current_enrollment__gte=models.F('capacity') * 0.9,
    capacity__isnull=False
)
```

## Indexing Strategy Comparison

### Academic Domain (AcademicYear)
```python
indexes = [
    models.Index(fields=["is_current"], name="academic_year_is_current_idx"),
    models.Index(fields=["status"], name="academic_year_status_idx"),
    models.Index(fields=["start_year"], name="academic_year_start_year_idx"),
    models.Index(fields=["start_year", "end_year"], name="academic_year_period_idx"),
]
```

### Geography Domain (Locality)
```python
# No explicit indexes in models
# Relies on db_index=True for FKs and unique fields
```

### School Operations (School) - Proposed
```python
indexes = [
    models.Index(fields=["code"], name="school_code_idx"),
    models.Index(fields=["type", "status"], name="school_type_status_idx"),
    models.Index(fields=["level"], name="school_level_idx"),
    models.Index(fields=["locality", "name"], name="school_locality_name_idx"),
    models.Index(fields=["status", "is_active"], name="school_status_active_idx"),
    models.Index(fields=["current_enrollment"], name="school_enrollment_idx"),
]
```

**Rationale**:
- Similar complexity to AcademicYear (operational entity)
- More complex than Geography (reference data)
- Composite indexes for common query patterns
- Enrollment index for reporting queries

## Validation Patterns

### Academic Domain Example (AcademicYear)
```python
def clean(self):
    super().clean()
    
    # Validate year sequence
    if self.end_year != self.start_year + 1:
        raise ValidationError({"end_year": "End year must be start_year + 1"})
    
    # Only one current year
    if self.is_current:
        existing_current = (
            AcademicYear.active.filter(is_current=True)
            .exclude(pk=self.pk)
            .exists()
        )
        if existing_current:
            raise ValidationError({"is_current": "Only one academic year can be current"})
```

### School Domain - Proposed
```python
def clean(self):
    super().clean()
    
    # Validate capacity vs enrollment
    if self.capacity and self.current_enrollment > self.capacity:
        raise ValidationError({
            "current_enrollment": f"Enrollment ({self.current_enrollment}) exceeds capacity ({self.capacity})"
        })
    
    # Validate founded year
    if self.founded_year and self.founded_year > timezone.now().year:
        raise ValidationError({
            "founded_year": "Founded year cannot be in the future"
        })
    
    # Validate locality is not deleted
    if self.locality and self.locality.is_deleted:
        raise ValidationError({
            "locality": "Cannot assign a deleted locality"
        })
    
    # Validate users are active
    if self.director and not self.director.is_active:
        raise ValidationError({
            "director": "Director must be an active user"
        })
```

**Pattern Consistency**:
- Always call `super().clean()`
- Use ValidationError with dict for field-specific errors
- Validate business rules, not just data types
- Check related objects' state

## Settings Pattern (New)

**School Introduces JSONField Settings**:
```python
settings = models.JSONField(
    default=dict,
    blank=True,
    help_text=_('School-specific configuration settings')
)
```

**Not Used in Other Domains** (Yet):
- AcademicYear: No settings field (all fields are explicit)
- Geography: No settings field (reference data)
- Account: No settings field (user preferences elsewhere)

**Future Application**:
This pattern could be adopted for:
- User preferences (Account domain)
- AcademicYear customization (Academic domain)
- System configuration (Shared domain)

**Benefits**:
- Extensibility without migrations
- School-specific customization
- Hierarchical configuration
- Type safety with validation

**Implementation**:
```python
# Helper methods on model
def get_setting(self, key_path: str, default=None):
    """Get setting using dot notation: 'academic.default_term_type'"""
    keys = key_path.split('.')
    value = self.settings
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
    return value if value is not None else default

def set_setting(self, key_path: str, value) -> None:
    """Set setting using dot notation."""
    keys = key_path.split('.')
    current = self.settings
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
```

## Migration Considerations

### No Breaking Changes Required
The School model **does not require changes** to existing domains:

**Geography Domain**:
- ✓ School uses existing Locality model
- ✓ No new fields needed in geography models
- ✓ Reverse relationship auto-created (locality.schools)

**Account Domain**:
- ✓ School uses existing CustomUser model
- ✓ No new fields needed in user model
- ✓ Reverse relationships auto-created (user.schools_as_director, etc.)

**Academic Domain**:
- ✓ No immediate dependency
- ✓ Future SchoolYear model will bridge School + AcademicYear
- ✓ No changes to AcademicYear model needed

### Migration Order
```bash
1. Create school_operations migrations (School model)
2. Apply migrations (no dependencies on academic/geography/account changes)
3. Seed sample data (optional)
4. Future: Add SchoolYear model (depends on School + AcademicYear)
```

## Summary

The School model follows established patterns while introducing domain-specific features:

**Follows Patterns**:
- ✓ AuditModel for business entities
- ✓ Soft delete with conditional unique constraints
- ✓ PROTECT for critical FK relationships
- ✓ SET_NULL for optional user relationships
- ✓ Status enum pattern
- ✓ Indexed fields for performance
- ✓ clean() and save() validation

**New Patterns**:
- ⭐ JSONField for extensible settings
- ⭐ Capacity management (enrollment vs capacity)
- ⭐ Scoped uniqueness (name per locality)
- ⭐ Multiple user role relationships

**Integration Points**:
- → Geography: Required dependency (locality)
- → Account: Optional dependencies (director, registrar)
- → Academic: Future dependency (via SchoolYear)
- ← Enrollments: Future dependents
- ← Staff: Future dependents
