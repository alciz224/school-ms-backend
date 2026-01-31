# School Model - Quick Overview

## Model Structure

```
School (AuditModel)
├── Identity
│   ├── code: CharField(20) [unique, indexed]
│   ├── name: CharField(200) [indexed]
│   └── short_name: CharField(100) [optional]
│
├── Classification
│   ├── type: CharField [PUBLIC, PRIVATE, COMMUNITY, ISLAMIC, CONFESSIONAL]
│   ├── level: CharField [PRESCHOOL, PRIMARY, SECONDARY, PRIMARY_SECONDARY, COMPLETE]
│   └── status: CharField [DRAFT, ACTIVE, SUSPENDED, CLOSED]
│
├── Relationships
│   ├── locality: FK → Geography.Locality [PROTECT, required]
│   ├── director: FK → Account.CustomUser [SET_NULL, optional]
│   └── registrar: FK → Account.CustomUser [SET_NULL, optional]
│
├── Contact
│   ├── email: EmailField [optional]
│   ├── phone: CharField(20) [optional]
│   ├── phone_secondary: CharField(20) [optional]
│   ├── website: URLField [optional]
│   ├── address_line1: CharField(255) [optional]
│   ├── address_line2: CharField(255) [optional]
│   └── postal_code: CharField(20) [optional]
│
├── Operations
│   ├── founded_year: PositiveIntegerField [optional]
│   ├── capacity: PositiveIntegerField [optional]
│   └── current_enrollment: PositiveIntegerField [default=0, indexed]
│
├── Extensibility
│   ├── settings: JSONField [default={}]
│   └── notes: TextField [optional]
│
└── Audit (inherited from AuditModel)
    ├── created_at, updated_at
    ├── created_by, updated_by, deleted_by
    └── is_active, is_deleted, deleted_at
```

## Domain Relationships

```
┌──────────────────────────────────────────────────────────┐
│                    SCHOOL MODEL                          │
│                  (school_operations)                     │
└────────────┬─────────────────────────────┬───────────────┘
             │                             │
             │ Depends On                  │ Provides Foundation For
             │                             │
    ┌────────┴────────┐          ┌─────────┴──────────┐
    │                 │          │                    │
    ▼                 ▼          ▼                    ▼
┌─────────┐    ┌──────────┐  ┌──────────┐    ┌──────────────┐
│Geography│    │ Account  │  │SchoolYear│    │  Enrollment  │
│  Domain │    │  Domain  │  │ (future) │    │   (future)   │
│         │    │          │  │          │    │              │
│Locality │    │CustomUser│  │          │    │              │
└─────────┘    └──────────┘  └──────────┘    └──────────────┘
```

## Key Design Decisions

### 1. Base Model Choice: AuditModel ✓
**Why**: Schools are business entities requiring full audit capabilities
- ✓ Timestamp tracking (created_at, updated_at)
- ✓ Author tracking (created_by, updated_by, deleted_by)
- ✓ Soft delete capability (is_deleted, deleted_at)
- ✓ Activation management (is_active)
- ✓ Multiple managers (objects, active, deleted, inactive)

**Alternative Considered**: GeographyBaseModel
- ✗ No is_active field (schools need activation control)
- ✗ Missing activation/deactivation workflow

### 2. Primary Key: Auto-incrementing Integer (Django default) ✓
**Why**: Simple, performant, and consistent with other models
- ✓ AcademicYear, Subject, Cycle all use integer PKs
- ✓ Better performance for joins and indexing
- ✓ Simpler URL structure (/schools/1/)
- ✓ code field provides human-readable unique identifier

**Alternative Considered**: UUID
- ✗ Only CustomUser uses UUID (special auth requirements)
- ✗ Larger index size, slower joins
- ~ Would provide better distributed ID generation (not needed)

### 3. Locality Relationship: PROTECT ✓
**Why**: Preserves data integrity
- ✓ Schools cannot exist without location
- ✓ Prevents accidental deletion of geography data
- ✓ Consistent with geography domain pattern
- ✓ Matches Region→Country, Unit→Region patterns

### 4. User Relationships: SET_NULL ✓
**Why**: Flexible staff management
- ✓ Schools can exist without assigned director/registrar
- ✓ Users can be removed without affecting school
- ✓ Historical data preserved (audit trail shows who created)
- ✓ Allows role transitions

### 5. Settings Field: JSONField ✓
**Why**: Future-proof extensibility
- ✓ Avoid schema migrations for new settings
- ✓ School-specific configuration
- ✓ Supports hierarchical configuration
- ✓ Default structure provides guidance

**Structure**:
```json
{
  "academic": { "default_term_type": "TRIMESTER", "pass_mark": 10 },
  "operations": { "allow_online_enrollment": true },
  "localization": { "timezone": "Africa/Conakry", "primary_language": "fr" },
  "custom": { }
}
```

### 6. Code Generation: Auto-generated but overridable ✓
**Why**: Balance between automation and flexibility
- ✓ Default format can be configured
- ✓ Manual codes allowed for special cases
- ✓ Unique constraint ensures no conflicts
- ✓ Indexed for fast lookups

### 7. Name Uniqueness: Scoped to Locality ✓
**Why**: Realistic business requirement
- ✓ Different localities can have "École Primaire de X"
- ✓ Within same locality, names must be unique
- ✓ Prevents duplicate registrations in same area
- ✓ Soft delete condition preserves history

## Indexes Strategy

**Performance-Critical Queries**:
1. Search by code: `school_code_idx`
2. Filter by type + status: `school_type_status_idx`
3. Filter by level: `school_level_idx`
4. Search within locality: `school_locality_name_idx`
5. Active schools: `school_status_active_idx`
6. Enrollment reporting: `school_enrollment_idx`

**Query Examples**:
```python
# Fast: Uses school_type_status_idx
School.objects.filter(type='PUBLIC', status='ACTIVE')

# Fast: Uses school_locality_name_idx
School.objects.filter(locality=loc, name__icontains='Primaire')

# Fast: Uses school_enrollment_idx
School.objects.filter(current_enrollment__gt=500)
```

## Status Workflow

```
         ┌──────────────────────────────────────────┐
         │                                          │
         │            activate()                    │
    ┌────▼───┐                               ┌──────┴────┐
    │  DRAFT │                               │  ACTIVE   │
    └────┬───┘                               └──────┬────┘
         │                                          │
         │                                          │ suspend()
         │                                          │
         │            close()                  ┌────▼────────┐
         ├────────────────────────────────────►│  SUSPENDED  │
         │                                     └────┬────────┘
         │                                          │
         │                                          │ close()
    ┌────▼──────────────────────────────────────────▼────┐
    │                    CLOSED                          │
    │               (No transitions out)                 │
    └───────────────────────────────────────────────────┘
```

**Business Rules**:
- **DRAFT**: Incomplete school profile
- **ACTIVE**: Fully operational, can enroll students
- **SUSPENDED**: Temporarily halted operations
- **CLOSED**: Permanently closed (no reopening)

## Comparison with Similar Models

### vs AcademicYear
| Feature | AcademicYear | School |
|---------|--------------|--------|
| Base | AuditModel | AuditModel |
| Scope | Global reference | Institution entity |
| Status | DRAFT/ACTIVE/ARCHIVED | DRAFT/ACTIVE/SUSPENDED/CLOSED |
| Unique | code (global) | code (global), name (per locality) |
| Relationships | None | Geography, Users |
| is_current | Yes (only one) | No (N/A) |

### vs Country (Geography)
| Feature | Country | School |
|---------|---------|--------|
| Base | GeographyBaseModel | AuditModel |
| is_active | No | Yes |
| Purpose | Reference data | Business entity |
| User links | No | Yes (director, registrar) |
| Settings | No | Yes (JSONField) |

## Future Extensions

### Phase 2 (After School Model Stable)
1. **SchoolYear** model
   - Links School + AcademicYear
   - School-specific year configuration
   - Term dates, enrollment periods

2. **Enrollment** model
   - Student enrollments per school year
   - Class/section assignments
   - Status tracking

3. **SchoolFacility** model
   - Classrooms, labs, library details
   - Capacity per facility
   - Condition tracking

### Phase 3 (Advanced Features)
1. **SchoolLicense** model
   - Government licenses/permits
   - Accreditation details
   - Expiry tracking

2. **SchoolInspection** model
   - Inspection reports
   - Compliance status
   - Action items

## Implementation Files

```
domain/school_operations/
├── constants.py              # SchoolType, SchoolLevel, SchoolStatus
├── validators.py             # validate_founded_year, validate_capacity, etc.
├── models/
│   ├── __init__.py          # Export School
│   └── school.py            # School model + SchoolManager
├── selectors/
│   ├── __init__.py
│   └── school.py            # Query functions
├── services/
│   ├── __init__.py
│   └── school.py            # Business logic (activate, suspend, etc.)
├── admin.py                 # Admin configuration
├── api/
│   ├── serializers/
│   │   └── school.py        # API serializers
│   ├── views/
│   │   └── school.py        # API views
│   └── urls.py              # API routes
├── management/commands/
│   └── seed_schools.py      # Sample data
└── tests/
    ├── test_models.py       # Model tests
    ├── test_services.py     # Service tests
    └── test_api.py          # API tests
```

## Next Steps

1. **Review & Feedback**: Gather team feedback on design
2. **Implementation**: Build model, tests, services
3. **Migration**: Create and apply database migration
4. **Testing**: Comprehensive test coverage
5. **Documentation**: API docs and usage examples
6. **Integration**: Connect to academic domain for SchoolYear
