# School Services and Selectors Usage Examples

This document provides examples of how to use the School services and selectors following DDD patterns.

## Table of Contents

1. [Services - Business Logic Layer](#services---business-logic-layer)
2. [Selectors - Query Layer](#selectors---query-layer)
3. [Common Use Cases](#common-use-cases)
4. [Best Practices](#best-practices)

---

## Services - Business Logic Layer

Services handle all business logic, validation, and state changes.

### Creating Schools

```python
from domain.school_operations.services import SchoolService
from domain.school_operations.constants import SchoolType, SchoolOwnership
from domain.geography.models import Locality

# Get locality
locality = Locality.objects.get(code='CONAKRY-001')

# Create a school with Guinea defaults
school = SchoolService.create(
    name="Lycée Filima",
    school_type=SchoolType.LYCEE,
    locality=locality,
    ownership=SchoolOwnership.PUBLIC,
    capacity=1200,
    phone="+224 622 00 00 00",
    email="contact@lyceefilima.gn",
    user=request.user
)

# Code is auto-generated: LYC-CONAKRY-001-001
print(f"Created school: {school.code}")
```

### Status Management Workflow

```python
from domain.school_operations.services import SchoolService
from domain.school_operations.selectors import SchoolSelector

# Get a draft school
school = SchoolSelector.get_by_code(code="LYC-CONAKRY-001-001")

# Activate school (DRAFT → ACTIVE)
school = SchoolService.activate(school=school, user=request.user)

# Suspend school temporarily (ACTIVE → SUSPENDED)
school = SchoolService.suspend(school=school, user=request.user)

# Reactivate school (SUSPENDED → ACTIVE)
school = SchoolService.reactivate(school=school, user=request.user)

# Close school permanently (ACTIVE/SUSPENDED → CLOSED)
# This removes director and registrar automatically
school = SchoolService.close(school=school, user=request.user)
```

### Settings Management

```python
from domain.school_operations.services import SchoolService

# Update a single setting using dot notation
SchoolService.update_setting(
    school=school,
    key='academic.grading_scale',
    value='20_point',
    user=request.user
)

# Update multiple settings (merge with existing)
SchoolService.update_settings(
    school=school,
    settings={
        'languages': {
            'instruction_language': 'french',
            'local_languages': ['pular', 'malinke']
        },
        'operations': {
            'lunch_program': True,
            'transportation': True
        }
    },
    merge=True,
    user=request.user
)

# Reset to Guinea defaults
SchoolService.reset_settings(school=school, user=request.user)
```

### Staff Management

```python
from domain.school_operations.services import SchoolService
from django.contrib.auth import get_user_model

User = get_user_model()

# Assign director (school must be ACTIVE)
director = User.objects.get(username='director.name')
school = SchoolService.assign_director(
    school=school,
    director=director,
    user=request.user
)

# Assign registrar
registrar = User.objects.get(username='registrar.name')
school = SchoolService.assign_registrar(
    school=school,
    registrar=registrar,
    user=request.user
)
```

### Capacity Management

```python
from domain.school_operations.services import SchoolService

# Update capacity with validation for school type
school = SchoolService.update_capacity(
    school=school,
    capacity=1500,  # Validated against school type ranges
    user=request.user
)
```

### Code Generation

```python
from domain.school_operations.services import SchoolService

# Regenerate school code (useful after type/locality change)
school = SchoolService.regenerate_code(
    school=school,
    user=request.user
)
```

### Deletion and Restoration

```python
from domain.school_operations.services import SchoolService

# Soft delete (default)
SchoolService.delete(school=school, user=request.user)

# Hard delete (permanent)
SchoolService.delete(school=school, user=request.user, hard=True)

# Restore soft-deleted school
school = SchoolService.restore(school=school, user=request.user)
```

---

## Selectors - Query Layer

Selectors handle all read operations and queries.

### Basic Queries

```python
from domain.school_operations.selectors import SchoolSelector

# Get all schools (excluding soft-deleted)
schools = SchoolSelector.get_all()

# Include soft-deleted schools
schools = SchoolSelector.get_all(include_deleted=True)

# Get by ID
school = SchoolSelector.get_by_id(school_id=1)

# Get by code
school = SchoolSelector.get_by_code(code="LYC-FILIMA-001")
```

### Status Queries

```python
from domain.school_operations.selectors import SchoolSelector
from domain.school_operations.constants import SchoolStatus

# Get active schools
active_schools = SchoolSelector.get_active()

# Get by specific status
draft_schools = SchoolSelector.get_draft()
suspended_schools = SchoolSelector.get_suspended()
closed_schools = SchoolSelector.get_closed()

# Get operational schools (alias for active)
operational = SchoolSelector.get_operational()
```

### Geographic Queries

```python
from domain.school_operations.selectors import SchoolSelector
from domain.geography.models import Locality, RegionAdministrative

# Get schools by locality
locality = Locality.objects.get(code='CONAKRY-001')
schools = SchoolSelector.get_by_locality(locality=locality)

# Get schools by region
region = RegionAdministrative.objects.get(code='CONAKRY')
schools = SchoolSelector.get_by_region(region=region)
```

### Type and Ownership Queries

```python
from domain.school_operations.selectors import SchoolSelector
from domain.school_operations.constants import SchoolType, SchoolOwnership

# Get schools by type
lycees = SchoolSelector.get_by_type(school_type=SchoolType.LYCEE)
primary_schools = SchoolSelector.get_by_type(school_type=SchoolType.PRIMAIRE)

# Get by ownership
public_schools = SchoolSelector.get_public_schools()
private_schools = SchoolSelector.get_private_schools()

# Get by specific ownership type
community_schools = SchoolSelector.get_by_ownership(
    ownership=SchoolOwnership.COMMUNITY
)
```

### Capacity Queries

```python
from domain.school_operations.selectors import SchoolSelector

# Get schools within capacity range
large_schools = SchoolSelector.get_by_capacity_range(
    min_capacity=1000,
    max_capacity=2000
)

# Get schools above minimum capacity
schools = SchoolSelector.get_by_capacity_range(min_capacity=500)
```

### Staff Queries

```python
from domain.school_operations.selectors import SchoolSelector

# Get schools with assigned staff
schools_with_staff = SchoolSelector.get_with_staff()

# Get schools without staff
schools_without_staff = SchoolSelector.get_without_staff()

# Get schools by director
director_schools = SchoolSelector.get_by_director(director=user)

# Get schools by registrar
registrar_schools = SchoolSelector.get_by_registrar(registrar=user)
```

### Search and Filtering

```python
from domain.school_operations.selectors import SchoolSelector
from domain.school_operations.constants import SchoolType, SchoolStatus

# Search by name, code, or address
schools = SchoolSelector.search(query="Lycée")

# Complex filtering
filtered_schools = SchoolSelector.filter_schools(
    region=region,
    school_type=SchoolType.LYCEE,
    ownership=SchoolOwnership.PUBLIC,
    status=SchoolStatus.ACTIVE,
    min_capacity=500,
    has_staff=True
)
```

### Statistics and Analytics

```python
from domain.school_operations.selectors import SchoolSelector

# Get overall statistics
stats = SchoolSelector.get_statistics()
# Returns: {
#     'total': 150,
#     'active': 120,
#     'suspended': 10,
#     'draft': 15,
#     'closed': 5,
#     'public': 100,
#     'private': 50,
#     'with_director': 110,
#     'with_registrar': 115,
#     'avg_capacity': 850.5
# }

# Statistics for specific locality
stats = SchoolSelector.get_statistics(locality=locality)

# Statistics for specific region
stats = SchoolSelector.get_statistics(region=region)

# Statistics by school type
type_stats = SchoolSelector.get_by_type_statistics()
# Returns: {
#     'primaire': 50,
#     'college': 40,
#     'lycee': 30,
#     ...
# }

# Statistics by region
region_stats = SchoolSelector.get_by_region_statistics()
# Returns QuerySet with region annotations

# Capacity statistics
capacity_stats = SchoolSelector.get_capacity_statistics(region=region)
# Returns: {
#     'total_capacity': 120000,
#     'avg_capacity': 800,
#     'max_capacity': 2000,
#     'min_capacity': 100,
#     'schools_with_capacity': 150
# }
```

### Utility Queries

```python
from domain.school_operations.selectors import SchoolSelector

# Check if code exists
exists = SchoolSelector.exists_by_code(code="LYC-FILIMA-001")

# Check excluding specific school (for updates)
exists = SchoolSelector.exists_by_code(
    code="LYC-FILIMA-001",
    exclude_id=5
)

# Get recent schools
recent = SchoolSelector.get_recent(limit=10)

# Get schools needing attention (suspended or active without staff)
needs_attention = SchoolSelector.get_schools_needing_attention()
```

---

## Common Use Cases

### Use Case 1: School Registration Flow

```python
from domain.school_operations.services import SchoolService
from domain.school_operations.selectors import SchoolSelector
from domain.school_operations.constants import SchoolType, SchoolOwnership

def register_new_school(data, user):
    """Complete school registration workflow."""
    
    # 1. Check if code already exists (if provided)
    if data.get('code'):
        if SchoolSelector.exists_by_code(code=data['code']):
            raise ValidationError("School code already exists")
    
    # 2. Create school in DRAFT status
    school = SchoolService.create(
        name=data['name'],
        school_type=data['school_type'],
        locality=data['locality'],
        ownership=data.get('ownership', SchoolOwnership.PUBLIC),
        capacity=data.get('capacity'),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        user=user
    )
    
    # 3. Configure Guinea-specific settings
    SchoolService.update_settings(
        school=school,
        settings={
            'languages': {
                'instruction_language': 'french',
                'local_languages': ['pular']
            },
            'academic': {
                'grading_scale': '20_point',
                'academic_year_start_month': 10
            }
        },
        user=user
    )
    
    # 4. Activate school
    school = SchoolService.activate(school=school, user=user)
    
    return school
```

### Use Case 2: Regional School Report

```python
from domain.school_operations.selectors import SchoolSelector
from domain.geography.models import RegionAdministrative

def generate_regional_report(region_code):
    """Generate comprehensive report for a region."""
    
    region = RegionAdministrative.objects.get(code=region_code)
    
    # Get all schools in region
    schools = SchoolSelector.get_by_region(region=region)
    
    # Get statistics
    stats = SchoolSelector.get_statistics(region=region)
    capacity_stats = SchoolSelector.get_capacity_statistics(region=region)
    
    # Get schools needing attention
    needs_attention = SchoolSelector.filter_schools(
        region=region,
        status=SchoolStatus.SUSPENDED
    )
    
    schools_without_staff = SchoolSelector.filter_schools(
        region=region,
        status=SchoolStatus.ACTIVE,
        has_staff=False
    )
    
    return {
        'region': region,
        'total_schools': schools.count(),
        'statistics': stats,
        'capacity': capacity_stats,
        'suspended_schools': needs_attention.count(),
        'schools_without_staff': schools_without_staff.count(),
    }
```

### Use Case 3: Bulk School Status Update

```python
from domain.school_operations.services import SchoolService
from domain.school_operations.selectors import SchoolSelector
from django.db import transaction

@transaction.atomic
def suspend_schools_in_locality(locality, reason, user):
    """Suspend all active schools in a locality."""
    
    schools = SchoolSelector.filter_schools(
        locality=locality,
        status=SchoolStatus.ACTIVE
    )
    
    suspended_count = 0
    for school in schools:
        try:
            SchoolService.suspend(school=school, user=user)
            suspended_count += 1
        except ValidationError as e:
            # Log error but continue
            print(f"Could not suspend {school.code}: {e}")
    
    return suspended_count
```

### Use Case 4: School Dashboard Data

```python
from domain.school_operations.selectors import SchoolSelector

def get_dashboard_data():
    """Get data for school management dashboard."""
    
    return {
        'overview': {
            'total': SchoolSelector.get_all().count(),
            'active': SchoolSelector.get_active().count(),
            'suspended': SchoolSelector.get_suspended().count(),
            'draft': SchoolSelector.get_draft().count(),
        },
        'by_type': SchoolSelector.get_by_type_statistics(),
        'by_region': list(SchoolSelector.get_by_region_statistics().values(
            'name', 'code', 'total_schools', 'active_schools'
        )),
        'capacity': SchoolSelector.get_capacity_statistics(),
        'needs_attention': SchoolSelector.get_schools_needing_attention().count(),
        'recent': list(SchoolSelector.get_recent(limit=5).values(
            'id', 'name', 'code', 'created_at'
        ))
    }
```

---

## Best Practices

### 1. Always Use Services for Mutations

❌ **Don't do this:**
```python
school.status = SchoolStatus.ACTIVE
school.save()
```

✅ **Do this:**
```python
SchoolService.activate(school=school, user=request.user)
```

### 2. Use Selectors for All Queries

❌ **Don't do this:**
```python
schools = School.objects.filter(status=SchoolStatus.ACTIVE)
```

✅ **Do this:**
```python
schools = SchoolSelector.get_active()
```

### 3. Use Keyword Arguments

All service methods use keyword-only arguments for clarity:

✅ **Correct:**
```python
school = SchoolService.create(
    name="Lycée Test",
    school_type=SchoolType.LYCEE,
    locality=locality,
    user=request.user
)
```

### 4. Handle Validation Errors

```python
from django.core.exceptions import ValidationError

try:
    school = SchoolService.activate(school=school, user=request.user)
except ValidationError as e:
    # Handle error appropriately
    return Response({'error': str(e)}, status=400)
```

### 5. Use Transactions for Complex Operations

```python
from django.db import transaction

@transaction.atomic
def complex_operation(school, user):
    school = SchoolService.update_capacity(school=school, capacity=1500, user=user)
    school = SchoolService.assign_director(school=school, director=director, user=user)
    return school
```

### 6. Leverage Type Hints

The services and selectors use type hints for better IDE support:

```python
from domain.school_operations.models import School
from domain.geography.models import Locality

def my_function(school: School, locality: Locality) -> School:
    return SchoolService.update(
        school=school,
        locality=locality,
        user=request.user
    )
```

### 7. Use Include_deleted Carefully

Only use `include_deleted=True` when you specifically need soft-deleted records:

```python
# For admin interfaces or recovery operations
all_schools = SchoolSelector.get_all(include_deleted=True)

# For normal operations (default)
active_schools = SchoolSelector.get_active()
```

---

## Integration with Views

### Django Rest Framework Example

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from domain.school_operations.services import SchoolService
from domain.school_operations.selectors import SchoolSelector

class SchoolViewSet(viewsets.ViewSet):
    
    def list(self, request):
        schools = SchoolSelector.get_all()
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        try:
            school = SchoolService.create(
                name=request.data['name'],
                school_type=request.data['school_type'],
                locality_id=request.data['locality'],
                user=request.user
            )
            serializer = SchoolSerializer(school)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        school = SchoolSelector.get_by_id(school_id=pk)
        if not school:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            school = SchoolService.activate(school=school, user=request.user)
            serializer = SchoolSerializer(school)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

## Additional Notes

- All services automatically track `created_by`, `updated_by`, `deleted_by`
- School codes are auto-generated based on type and locality
- Settings are validated against Guinea-specific configuration
- Status transitions enforce business rules
- Geographic relationships are protected (can't delete referenced localities)
- Capacity is validated against school type ranges

For more information, see:
- `domain/school_operations/models/school.py` - Model implementation
- `domain/school_operations/constants.py` - Constants and choices
- `domain/school_operations/validators.py` - Validation rules
