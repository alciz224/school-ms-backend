# School Services & Selectors - Quick Reference

## Import Statements

```python
from domain.school_operations.services import SchoolService
from domain.school_operations.selectors import SchoolSelector
from domain.school_operations.constants import SchoolType, SchoolStatus, SchoolOwnership
```

---

## Services (Mutations)

### Create
```python
school = SchoolService.create(
    name="School Name",
    school_type=SchoolType.LYCEE,
    locality=locality,
    user=request.user
)
```

### Update
```python
school = SchoolService.update(
    school=school,
    name="New Name",
    capacity=1500,
    user=request.user
)
```

### Status Management
```python
# DRAFT → ACTIVE
school = SchoolService.activate(school=school, user=request.user)

# ACTIVE → SUSPENDED
school = SchoolService.suspend(school=school, user=request.user)

# SUSPENDED → ACTIVE
school = SchoolService.reactivate(school=school, user=request.user)

# ACTIVE/SUSPENDED → CLOSED
school = SchoolService.close(school=school, user=request.user)
```

### Staff
```python
school = SchoolService.assign_director(school=school, director=user, user=request.user)
school = SchoolService.assign_registrar(school=school, registrar=user, user=request.user)
```

### Settings
```python
# Single setting
SchoolService.update_setting(school=school, key='academic.grading_scale', value='20_point', user=request.user)

# Multiple settings
SchoolService.update_settings(school=school, settings={...}, merge=True, user=request.user)

# Reset to defaults
SchoolService.reset_settings(school=school, user=request.user)
```

### Other Operations
```python
# Update capacity
school = SchoolService.update_capacity(school=school, capacity=1500, user=request.user)

# Regenerate code
school = SchoolService.regenerate_code(school=school, user=request.user)

# Delete
SchoolService.delete(school=school, user=request.user)  # Soft delete
SchoolService.delete(school=school, user=request.user, hard=True)  # Hard delete

# Restore
school = SchoolService.restore(school=school, user=request.user)
```

---

## Selectors (Queries)

### Basic Queries
```python
schools = SchoolSelector.get_all()
school = SchoolSelector.get_by_id(school_id=1)
school = SchoolSelector.get_by_code(code="LYC-001")
schools = SchoolSelector.search(query="Lycée")
```

### By Status
```python
active = SchoolSelector.get_active()
draft = SchoolSelector.get_draft()
suspended = SchoolSelector.get_suspended()
closed = SchoolSelector.get_closed()
```

### By Geography
```python
schools = SchoolSelector.get_by_locality(locality=locality)
schools = SchoolSelector.get_by_region(region=region)
```

### By Type/Ownership
```python
lycees = SchoolSelector.get_by_type(school_type=SchoolType.LYCEE)
public = SchoolSelector.get_public_schools()
private = SchoolSelector.get_private_schools()
```

### By Capacity
```python
schools = SchoolSelector.get_by_capacity_range(min_capacity=500, max_capacity=1500)
```

### By Staff
```python
with_staff = SchoolSelector.get_with_staff()
without_staff = SchoolSelector.get_without_staff()
my_schools = SchoolSelector.get_by_director(director=user)
```

### Complex Filtering
```python
schools = SchoolSelector.filter_schools(
    region=region,
    school_type=SchoolType.LYCEE,
    status=SchoolStatus.ACTIVE,
    min_capacity=500,
    has_staff=True
)
```

### Statistics
```python
stats = SchoolSelector.get_statistics()
stats = SchoolSelector.get_statistics(region=region)
type_stats = SchoolSelector.get_by_type_statistics()
region_stats = SchoolSelector.get_by_region_statistics()
capacity_stats = SchoolSelector.get_capacity_statistics()
```

### Utilities
```python
exists = SchoolSelector.exists_by_code(code="LYC-001")
recent = SchoolSelector.get_recent(limit=10)
attention = SchoolSelector.get_schools_needing_attention()
```

---

## Constants

### School Types
```python
SchoolType.PRESCOLAIRE   # Pre-school
SchoolType.PRIMAIRE      # Primary
SchoolType.COLLEGE       # Lower secondary
SchoolType.LYCEE         # Upper secondary
SchoolType.TECHNIQUE     # Technical
SchoolType.SUPERIEUR     # Higher education
SchoolType.FORMATION_PROF # Professional training
```

### School Status
```python
SchoolStatus.DRAFT      # Planning phase
SchoolStatus.ACTIVE     # Operational
SchoolStatus.SUSPENDED  # Temporarily closed
SchoolStatus.CLOSED     # Permanently closed
```

### Ownership Types
```python
SchoolOwnership.PUBLIC     # Government
SchoolOwnership.PRIVATE    # Private
SchoolOwnership.COMMUNITY  # Community-based
SchoolOwnership.RELIGIOUS  # Religious
SchoolOwnership.NGO        # NGO-operated
```

---

## Common Patterns

### DRF ViewSet Example
```python
class SchoolViewSet(viewsets.ViewSet):
    def list(self, request):
        schools = SchoolSelector.get_active()
        return Response(SchoolSerializer(schools, many=True).data)
    
    def create(self, request):
        school = SchoolService.create(
            name=request.data['name'],
            school_type=request.data['school_type'],
            locality_id=request.data['locality'],
            user=request.user
        )
        return Response(SchoolSerializer(school).data, status=201)
```

### Error Handling
```python
from django.core.exceptions import ValidationError

try:
    school = SchoolService.activate(school=school, user=request.user)
except ValidationError as e:
    return Response({'error': str(e)}, status=400)
```

### Transaction Usage
```python
from django.db import transaction

@transaction.atomic
def bulk_operation(schools, user):
    for school in schools:
        SchoolService.update_capacity(school=school, capacity=1500, user=user)
```

---

## Rules & Validations

### Status Transitions
- ✅ DRAFT → ACTIVE
- ✅ ACTIVE → SUSPENDED
- ✅ SUSPENDED → ACTIVE
- ✅ ACTIVE → CLOSED
- ✅ SUSPENDED → CLOSED
- ❌ CLOSED → (any other status)
- ❌ DRAFT → SUSPENDED

### Business Rules
- Only ACTIVE schools can have director/registrar
- Closing a school removes all staff
- Cannot use deleted localities
- Capacity must match school type ranges
- Code is unique across all schools

### Auto-Generated Fields
- **Code**: Auto-generated as `TYPE-LOCALITY-###` (e.g., `LYC-CONAKRY-001`)
- **Settings**: Initialized with Guinea defaults
- **Audit fields**: Automatically tracked

---

## Settings Structure

```python
{
    'languages': {
        'instruction_language': 'french',
        'local_languages': ['pular', 'malinke']
    },
    'academic': {
        'grading_scale': '20_point',
        'academic_year_start_month': 10
    },
    'operations': {
        'lunch_program': False,
        'transportation': False,
        'boarding': False
    }
}
```

Access with dot notation:
```python
value = school.get_setting('academic.grading_scale')
SchoolService.update_setting(school, 'operations.lunch_program', True, user)
```

---

## Best Practices

### ✅ DO
- Use services for all mutations
- Use selectors for all queries
- Always pass `user` parameter
- Use keyword arguments
- Handle ValidationErrors
- Use transactions for complex operations

### ❌ DON'T
- Don't bypass services (e.g., `school.status = ...`)
- Don't use `School.objects` directly in views
- Don't forget error handling
- Don't mix queries and mutations

---

## See Also
- `USAGE_EXAMPLES.md` - Detailed examples and use cases
- `SERVICES_SELECTORS_SUMMARY.md` - Complete implementation details
- `models/school.py` - School model reference
- `constants.py` - All constants and choices
