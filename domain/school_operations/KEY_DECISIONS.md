# School Model - Key Design Decisions

## Executive Summary

This document captures the critical design decisions made for the School model, the foundational entity of the school_operations domain.

## 1. Base Model Selection

**Decision**: Use `AuditModel` as the base class

**Rationale**:
- Schools are business entities, not reference data
- Require full audit capabilities (who created, updated, deleted)
- Need activation/deactivation workflow (is_active field)
- Require soft delete functionality

**Alternatives Considered**:
- ❌ GeographyBaseModel: Lacks is_active field (inappropriate for operational entities)
- ❌ BaseModel: Lacks author tracking and soft delete
- ✅ AuditModel: Perfect fit for business entities with full audit needs

**Pattern Consistency**: 
- Matches AcademicYear, Subject, Cycle (all business entities)
- Different from Country, Region (reference data uses GeographyBaseModel)

---

## 2. Primary Key Type

**Decision**: Auto-incrementing Integer (Django default)

**Rationale**:
- Consistent with all other models except CustomUser
- Better performance for joins and indexing
- Simpler URL structure (/schools/1/)
- `code` field provides human-readable identifier

**Alternatives Considered**:
- ❌ UUID: Only justified for CustomUser (authentication requirements)
- ❌ Custom string PK: Adds complexity without benefit

---

## 3. Uniqueness Constraints

**Decision**: 
- `code`: Global unique (across all schools)
- `name`: Scoped unique (per locality only)

**Rationale**:
- Code serves as global identifier (like license plate)
- Name can repeat across different localities (realistic requirement)
- Example: "École Primaire" exists in many villages

**Implementation**:
```python
UniqueConstraint(
    fields=["code"],
    condition=Q(is_deleted=False),
    name="unique_school_code"
)
UniqueConstraint(
    fields=["locality", "name"],
    condition=Q(is_deleted=False),
    name="unique_school_name_per_locality"
)
```

---

## 4. Geography Relationship

**Decision**: `locality` FK with `on_delete=PROTECT` (required)

**Rationale**:
- Schools must have a physical location
- PROTECT prevents accidental deletion of geography data
- Consistent with geography domain pattern (Region→Country, Unit→Region)
- Provides automatic hierarchy access (Country→Region→Unit→Locality→School)

**Business Rule**: Cannot delete a locality that has schools

---

## 5. User Relationships

**Decision**: `director` and `registrar` FKs with `on_delete=SET_NULL` (optional)

**Rationale**:
- Schools can exist without assigned leadership
- Users can be removed without affecting school entity
- Flexible role transitions
- Audit trail preserved in created_by/updated_by

**Pattern**: Optional organizational relationships use SET_NULL

---

## 6. Status Workflow

**Decision**: Four-state model (DRAFT, ACTIVE, SUSPENDED, CLOSED)

**Status Definitions**:
- **DRAFT**: Incomplete profile, not operational
- **ACTIVE**: Fully operational, can enroll students
- **SUSPENDED**: Temporarily halted operations (can be restored)
- **CLOSED**: Permanently closed (no reopening, must create new school)

**Transitions**:
```
DRAFT → ACTIVE (requires complete profile)
ACTIVE ↔ SUSPENDED (can suspend/restore)
* → CLOSED (can close from any status, no return)
```

**Why Not Like AcademicYear?**:
- AcademicYear: DRAFT/ACTIVE/ARCHIVED (time-based)
- School: DRAFT/ACTIVE/SUSPENDED/CLOSED (operation-based)
- Different domain needs require different statuses

---

## 7. Settings Field (JSONField)

**Decision**: Use JSONField with default structure

**Rationale**:
- Future-proof extensibility without schema migrations
- School-specific configuration (term types, grading scales)
- Hierarchical organization (academic, operations, localization)
- Default structure provides guidance

**Structure**:
```json
{
  "academic": { "default_term_type": "TRIMESTER", "pass_mark": 10 },
  "operations": { "allow_online_enrollment": true },
  "localization": { "timezone": "Africa/Conakry", "primary_language": "fr" },
  "custom": { }
}
```

**Pattern**: New pattern for this codebase (can be adopted by other domains)

---

## 8. Capacity Management

**Decision**: Separate `capacity` and `current_enrollment` fields with check constraint

**Fields**:
- `capacity`: Optional max student capacity
- `current_enrollment`: Calculated field (updated by enrollment services)

**Constraint**:
```python
CheckConstraint(
    check=Q(current_enrollment__lte=F('capacity')) | Q(capacity__isnull=True),
    name="school_enrollment_within_capacity"
)
```

**Rationale**:
- Enforce business rule at database level
- Support schools without defined capacity (capacity=NULL)
- Provide enrollment tracking foundation

---

## 9. Code Generation Strategy

**Decision**: Auto-generated but overridable

**Behavior**:
- If code not provided: Generate from pattern (configurable)
- If code provided: Use as-is (with validation)
- Unique constraint prevents conflicts

**Rationale**:
- Automation for common case (reduce manual work)
- Flexibility for special cases (manual codes)
- Balance convenience and control

---

## 10. Index Strategy

**Decision**: Six strategic indexes

**Indexes**:
1. `school_code_idx` - Fast code lookups
2. `school_type_status_idx` - Common filtering pattern
3. `school_level_idx` - Level-based queries
4. `school_locality_name_idx` - Geographic + name search
5. `school_status_active_idx` - Active school queries
6. `school_enrollment_idx` - Reporting queries

**Rationale**:
- Based on expected query patterns
- Balance between query performance and write overhead
- Composite indexes for multi-column queries

---

## 11. Soft Delete Implementation

**Decision**: Use soft delete from AuditModel (is_deleted, deleted_at, deleted_by)

**Benefits**:
- Preserve historical data
- Enable undo/restore functionality
- Maintain referential integrity
- Support compliance requirements

**Constraint Pattern**: All unique constraints include `condition=Q(is_deleted=False)`

**Effect**: Deleted schools' codes/names can be reused by new schools

---

## 12. Address Fields

**Decision**: Multiple optional address fields (address_line1, address_line2, postal_code)

**Rationale**:
- Locality provides administrative hierarchy
- Address fields for street-level details
- All optional (some schools may not have formal addresses)
- Postal code optional (not universal in all regions)

**Alternative Considered**:
- ❌ Single text field: Less structured, harder to parse
- ✅ Multiple fields: Better for future integration (maps, mail systems)

---

## 13. Contact Information

**Decision**: Email, phone, phone_secondary, website (all optional)

**Rationale**:
- Not all schools have all contact methods
- Multiple phones common (main office + director)
- Website optional (many schools don't have one)

**Validation**: Phone uses international format validator (from account domain)

---

## 14. Founded Year

**Decision**: Optional PositiveIntegerField with future validation

**Rationale**:
- Historical tracking useful but not critical
- Many schools don't have formal founding records
- Validator prevents future dates
- Simple integer (no need for full date)

---

## 15. Constants Pattern

**Decision**: Use `models.TextChoices` for enums

**Example**:
```python
class SchoolType(models.TextChoices):
    PUBLIC = "PUBLIC", _("Public")
    PRIVATE = "PRIVATE", _("Private")
```

**Rationale**:
- Modern Django pattern (3.0+)
- Built-in validation
- Internationalization support
- Better than class constants (used in academic domain)

**Migration Path**: Academic domain could adopt this pattern in future

---

## Summary Table

| Aspect | Decision | Pattern Source | Rationale |
|--------|----------|----------------|-----------|
| Base Class | AuditModel | Academic domain | Business entity needs |
| PK Type | Integer | All except User | Performance & simplicity |
| Code Uniqueness | Global | Academic domain | Global identifier |
| Name Uniqueness | Scoped | Geography domain | Realistic requirement |
| Locality FK | PROTECT | Geography domain | Data integrity |
| User FKs | SET_NULL | Common pattern | Flexibility |
| Status | 4-state | Domain-specific | Operational needs |
| Settings | JSONField | New pattern | Extensibility |
| Soft Delete | Inherited | AuditModel | History preservation |
| Indexes | 6 strategic | Academic domain | Query optimization |

---

## Implementation Impact

### No Breaking Changes Required
- Geography models: ✅ No changes needed
- Account models: ✅ No changes needed
- Academic models: ✅ No changes needed (future integration via SchoolYear)

### Future Integration Points
1. **SchoolYear** (Phase 2): Bridge between School + AcademicYear
2. **Enrollment** (Phase 3): Student enrollments per school
3. **Staff** (Phase 4): Teacher/staff assignments

---

## Lessons Learned from Existing Patterns

### What We Adopted
✅ AuditModel for business entities
✅ PROTECT for critical relationships
✅ SET_NULL for optional relationships
✅ Soft delete with conditional constraints
✅ Strategic indexing
✅ clean() validation pattern

### What We Adapted
🔄 Status enum (domain-specific needs)
🔄 Uniqueness scope (realistic business rules)
🔄 TextChoices vs class constants (modern pattern)

### What We Introduced
⭐ JSONField for settings (new pattern)
⭐ Capacity management pattern
⭐ Multiple user role relationships
⭐ Scoped name uniqueness

---

## Decision Approval Status

**Review Date**: Pending
**Approved By**: Pending
**Status**: ✅ Design Complete, Ready for Review

**Next Step**: Team review and implementation approval
