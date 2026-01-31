# School Model Design Document

## Overview
The School model serves as the foundational entity for the school_operations domain. It represents a physical school institution and acts as the anchor point for all school-specific operations like SchoolYear, Enrollments, Class Sections, etc.

## Analysis of Existing Patterns

### Base Model Patterns
1. **AuditModel** (from `domain.shared.models.base`):
   - Used for business entities that need full audit capabilities
   - Includes: timestamps, author tracking, soft delete, activation status
   - Provides managers: objects, active, deleted, inactive, all_objects
   - Examples: AcademicYear, Subject, Cycle

2. **GeographyBaseModel** (from `domain.geography.models.base`):
   - Used for reference data without activation status
   - Includes: timestamps, author tracking, soft delete (no is_active)
   - Examples: Country, Region, Locality

3. **CustomUser** (from `domain.account.models.user`):
   - Uses UUID as primary key
   - Custom authentication model
   - Has verification fields and metadata

### Naming Conventions
- **Table names**: Lowercase, singular (e.g., `academic_year`, `subject`, `cycle`)
- **Field names**: Snake_case
- **Class names**: PascalCase
- **Constants**: UPPER_CASE

### Field Patterns
1. **Unique identifiers**: 
   - `code`: Short alphanumeric code (indexed, unique within scope)
   - `name`: Human-readable name (indexed, unique within scope)

2. **Constraints**:
   - UniqueConstraint with `condition=models.Q(is_deleted=False)` for soft-deleted records
   - Composite unique constraints for scoped uniqueness

3. **Indexes**:
   - Explicit indexes on frequently queried fields
   - Composite indexes for common query patterns
   - Status fields are indexed

4. **Foreign Keys**:
   - `on_delete=models.PROTECT` for critical relationships
   - `related_name` always specified
   - `verbose_name` with gettext_lazy for i18n

### Validation Patterns
- `clean()` method for business rule validation
- `save()` method calls `full_clean()` before saving
- Separate validator functions in validators.py for reusable rules
- ValidationError with dict for field-specific errors

### Constants Patterns
- Class-based constants with CHOICES attribute
- Use of `models.TextChoices` for Django's choice field pattern
- Stored in `constants.py` in domain app

## School Model Design

### Domain Context
**Bounded Context**: School Operations
**Aggregate Root**: School
**Purpose**: Represent a physical school institution with all its operational metadata

### Relationships

#### To Geography Domain (Required)
- **locality**: ForeignKey to Locality (PROTECT)
  - Defines the physical location of the school
  - Required field (schools must have a location)
  - Provides: country → region → administrative_unit → locality hierarchy

#### To Account Domain (Optional)
- **director**: ForeignKey to CustomUser (SET_NULL, optional)
  - School director/principal
  - Can be null (school might not have assigned director yet)
- **registrar**: ForeignKey to CustomUser (SET_NULL, optional)
  - School registrar/administrator
  - Can be null

### Core Fields

#### Identity Fields
1. **code** (CharField, max_length=20, unique, indexed)
   - Short alphanumeric code (e.g., "EPK-001", "LYC-CON-CENTRAL")
   - Auto-generated if not provided
   - Format: Can be customized per country/region
   - Unique across all schools (with soft delete condition)

2. **name** (CharField, max_length=200, indexed)
   - Official school name (e.g., "École Primaire de Kassapo")
   - Required, can be duplicated (different localities might have same name)
   - Scoped uniqueness: unique per locality + is_deleted=False

3. **short_name** (CharField, max_length=100, optional)
   - Short display name (e.g., "EP Kassapo")
   - For UI displays and reports

#### Classification Fields
4. **type** (CharField, choices, indexed)
   - School type: PUBLIC, PRIVATE, COMMUNITY, ISLAMIC, etc.
   - Enum in constants.py: SchoolType

5. **level** (CharField, choices, indexed)
   - Educational level offered: PRESCHOOL, PRIMARY, SECONDARY, MIXED
   - Determines which cycles can be activated
   - Enum in constants.py: SchoolLevel

6. **status** (CharField, choices, indexed, default='DRAFT')
   - Operational status: DRAFT, ACTIVE, SUSPENDED, CLOSED
   - Enum in constants.py: SchoolStatus
   - Business rules around status transitions

#### Contact Information
7. **email** (EmailField, optional)
   - School's official email
   - Can be null

8. **phone** (CharField, max_length=20, optional)
   - Primary phone number (international format)
   - Validator for phone format

9. **phone_secondary** (CharField, max_length=20, optional)
   - Secondary/alternate phone number

10. **website** (URLField, optional)
    - School website URL

11. **address_line1** (CharField, max_length=255, optional)
    - Street address line 1

12. **address_line2** (CharField, max_length=255, optional)
    - Street address line 2 (optional)

13. **postal_code** (CharField, max_length=20, optional)
    - Postal/ZIP code

#### Operational Metadata
14. **founded_year** (PositiveIntegerField, optional)
    - Year the school was established
    - Validator: Cannot be in the future

15. **capacity** (PositiveIntegerField, optional)
    - Maximum student capacity
    - Used for enrollment planning

16. **current_enrollment** (PositiveIntegerField, default=0)
    - Current number of enrolled students
    - Updated by enrollment services
    - Indexed for reporting

#### Settings (JSONField)
17. **settings** (JSONField, default=dict)
    - Extensible settings dictionary
    - Structure:
      ```json
      {
        "academic": {
          "default_term_type": "TRIMESTER",
          "grading_scale": "0-20",
          "pass_mark": 10
        },
        "operations": {
          "allow_online_enrollment": true,
          "require_uniform": true,
          "has_cafeteria": false,
          "has_library": true
        },
        "localization": {
          "timezone": "Africa/Conakry",
          "primary_language": "fr",
          "supported_languages": ["fr", "pular", "malinke"]
        },
        "custom": {}
      }
      ```

#### Notes
18. **notes** (TextField, optional)
    - Internal notes/comments about the school
    - Not displayed to public

### Inherited from AuditModel
- created_at, updated_at
- created_by, updated_by, deleted_by
- is_active, is_deleted, deleted_at
- All audit managers (objects, active, deleted, inactive, all_objects)

### Model Metadata

#### Meta Options
```python
db_table = "school"
verbose_name = "School"
verbose_name_plural = "Schools"
ordering = ["locality__administrative_unit__region", "name"]
```

#### Indexes
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

#### Constraints
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
    models.CheckConstraint(
        check=models.Q(current_enrollment__lte=models.F('capacity')) | models.Q(capacity__isnull=True),
        name="school_enrollment_within_capacity"
    ),
]
```

### Business Rules

1. **Activation**:
   - School must have: name, code, locality, type, level
   - Status must be ACTIVE
   - Cannot be is_deleted=True

2. **Status Transitions**:
   - DRAFT → ACTIVE: Requires complete profile
   - ACTIVE → SUSPENDED: Can be done anytime
   - SUSPENDED → ACTIVE: Can be restored
   - * → CLOSED: Can be closed from any status
   - CLOSED → *: Cannot reopen closed schools (must create new)

3. **Soft Delete**:
   - Cascade consideration: SchoolYear, Enrollments use PROTECT
   - Deleted schools cannot be activated
   - Code is freed for reuse by other schools

4. **Enrollment**:
   - current_enrollment <= capacity (if capacity is set)
   - Updated automatically by enrollment service

5. **Geography Validation**:
   - Locality must not be deleted
   - Locality provides full geographic hierarchy

6. **User Relationships**:
   - Director and registrar can be null
   - Users are not deleted when school is deleted (SET_NULL)
   - Users must be active (validation rule)

### Methods

#### Instance Methods
```python
def __str__(self) -> str:
    """Return school display name."""
    return f"{self.name} ({self.code})"

def get_full_address(self) -> str:
    """Return formatted full address including locality."""

def get_geographic_path(self) -> str:
    """Return full geographic path (Country > Region > Unit > Locality)."""

def can_activate(self) -> tuple[bool, list[str]]:
    """Check if school can be activated. Returns (bool, [errors])."""

def activate(self, user) -> None:
    """Activate the school with validation."""

def suspend(self, user, reason: str = "") -> None:
    """Suspend school operations."""

def close(self, user, reason: str) -> None:
    """Permanently close the school."""

def update_enrollment_count(self) -> int:
    """Recalculate and update current_enrollment. Returns new count."""

def get_available_capacity(self) -> int | None:
    """Return remaining capacity (capacity - enrollment) or None if no capacity set."""

def is_at_capacity(self) -> bool:
    """Check if school is at full capacity."""

def get_setting(self, key_path: str, default=None):
    """Get a setting value using dot notation (e.g., 'academic.default_term_type')."""

def set_setting(self, key_path: str, value) -> None:
    """Set a setting value using dot notation."""
```

#### Custom Manager Methods
```python
class SchoolManager(BaseManager):
    """Custom manager for School model."""
    
    def by_locality(self, locality):
        """Get schools in a specific locality."""
        
    def by_administrative_unit(self, unit):
        """Get schools in an administrative unit."""
        
    def by_region(self, region):
        """Get schools in a region."""
        
    def by_type(self, school_type):
        """Get schools by type."""
        
    def active_operational(self):
        """Get schools that are active and operational (status=ACTIVE)."""
        
    def at_capacity(self):
        """Get schools that are at full capacity."""
        
    def with_capacity(self):
        """Get schools with available capacity."""
```

### Constants (constants.py)

```python
class SchoolType(models.TextChoices):
    """School type classification."""
    PUBLIC = "PUBLIC", _("Public")
    PRIVATE = "PRIVATE", _("Private")
    COMMUNITY = "COMMUNITY", _("Community")
    ISLAMIC = "ISLAMIC", _("Islamic/Franco-Arabic")
    CONFESSIONAL = "CONFESSIONAL", _("Confessional/Religious")


class SchoolLevel(models.TextChoices):
    """Educational levels offered by the school."""
    PRESCHOOL = "PRESCHOOL", _("Preschool Only")
    PRIMARY = "PRIMARY", _("Primary Only")
    SECONDARY = "SECONDARY", _("Secondary Only")
    PRIMARY_SECONDARY = "PRIMARY_SECONDARY", _("Primary + Secondary")
    COMPLETE = "COMPLETE", _("Complete (Preschool + Primary + Secondary)")


class SchoolStatus(models.TextChoices):
    """School operational status."""
    DRAFT = "DRAFT", _("Draft")
    ACTIVE = "ACTIVE", _("Active")
    SUSPENDED = "SUSPENDED", _("Suspended")
    CLOSED = "CLOSED", _("Closed")
```

### Validators (validators.py)

```python
def validate_founded_year(value: int) -> None:
    """Validate that founded year is not in the future."""

def validate_capacity(value: int) -> None:
    """Validate that capacity is reasonable (1-10000)."""

def validate_school_user(user) -> None:
    """Validate that user is active and not deleted."""
```

### Future Extensibility

#### Phase 2 Fields (Not in initial model)
- **accreditation**: Accreditation status and details
- **license_number**: Government license/registration number
- **inspection_data**: Latest inspection results
- **facilities**: Detailed facility information (classrooms, labs, etc.)
- **staff_count**: Total number of staff members
- **gps_coordinates**: Latitude/longitude for mapping

#### Related Models (Future)
- **SchoolYear**: School-specific academic year configuration
- **Enrollment**: Student enrollments per school year
- **ClassSection**: Classes/sections within the school
- **Staff**: School staff assignments
- **SchoolFacility**: Detailed facility management
- **SchoolDocument**: Document management (licenses, certificates)
- **SchoolContact**: Multiple contact persons

### Migration Strategy

1. **Initial Migration**: Create School model with all core fields
2. **Seed Data**: Command to create sample schools for testing
3. **Indexes**: All indexes created in initial migration
4. **Constraints**: All constraints created in initial migration

### Testing Considerations

1. **Model Tests**:
   - Field validation (required fields, formats)
   - Constraint validation (uniqueness, check constraints)
   - Business rule validation (status transitions, capacity)
   - Method behavior (activate, suspend, close)
   - Manager queries

2. **Integration Tests**:
   - Geography relationships
   - User relationships (director, registrar)
   - Audit trail (created_by, updated_by)

3. **Edge Cases**:
   - Soft delete and restore
   - Code generation conflicts
   - Capacity overflow
   - Status transition validation

## Implementation Checklist

- [ ] Create constants.py with enums
- [ ] Create validators.py with validation functions
- [ ] Create school.py model in models/
- [ ] Update models/__init__.py to export School
- [ ] Create initial migration
- [ ] Create admin.py configuration
- [ ] Create manager tests
- [ ] Create model tests
- [ ] Create seed command
- [ ] Create selectors
- [ ] Create services
- [ ] Create API serializers
- [ ] Create API views
- [ ] Update API urls
- [ ] Documentation

## References

- Similar models: AcademicYear, Subject (domain/academic)
- Base models: AuditModel (domain/shared/models/base.py)
- Geography models: Locality, Country (domain/geography/models)
- User model: CustomUser (domain/account/models/user.py)
