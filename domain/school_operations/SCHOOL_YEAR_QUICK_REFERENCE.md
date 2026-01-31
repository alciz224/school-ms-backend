# SchoolYear - Quick Reference Card

## Import Statements

```python
from domain.school_operations.models import SchoolYear
from domain.school_operations.services.school_year import SchoolYearService
from domain.school_operations.selectors.school_year import SchoolYearSelector
from domain.school_operations.constants import SchoolYearStatus
```

## Common Operations

### Create School Year (Guinea Defaults)

```python
school_year = SchoolYearService.create_school_year_for_guinea(
    school=school,
    academic_year=academic_year,
    capacity=500,
    user=request.user
)
```

### Create School Year (Custom Dates)

```python
school_year = SchoolYearService.create_school_year(
    school=school,
    academic_year=academic_year,
    start_date=date(2024, 10, 1),
    end_date=date(2025, 6, 30),
    enrollment_start_date=date(2024, 9, 1),
    enrollment_end_date=date(2024, 9, 30),
    capacity=500,
    user=request.user
)
```

### Status Transitions

```python
# Activate
school_year.activate(user=request.user)

# Complete
school_year.complete(user=request.user)

# Archive
school_year.archive(user=request.user)
```

### Query Operations

```python
# Get current for school
current = SchoolYearSelector.get_current_for_school(school)

# Get active for school
active = SchoolYearSelector.get_active_for_school(school)

# List all active
active_years = SchoolYearSelector.list_active()

# List with open enrollment
open_enrollment = SchoolYearSelector.list_with_open_enrollment()

# Search
results = SchoolYearSelector.search('Lycée', status='active')
```

### Enrollment Management

```python
# Check if enrollment is open
if school_year.is_enrollment_open():
    print("Enrollment is open")

# Check capacity
if school_year.has_capacity():
    available = school_year.available_capacity()
    print(f"{available} spots available")

# Update enrollment count (thread-safe)
school_year.increment_enrollment_count(1)
school_year.decrement_enrollment_count(1)
```

### Settings Management

```python
# Get setting
passing_grade = school_year.get_setting('assessment.passing_grade', 10.0)

# Update setting
school_year.update_setting('assessment.passing_grade', 12.0, user=request.user)

# Add holiday
school_year.add_holiday(
    'Christmas Break',
    date(2024, 12, 20),
    date(2025, 1, 5),
    user=request.user
)
```

### Statistics

```python
stats = SchoolYearService.get_enrollment_statistics(school_year)
# Returns:
# {
#     'total_capacity': 500,
#     'current_enrollment': 350,
#     'available_capacity': 150,
#     'enrollment_percentage': 70.0,
#     'is_full': False,
#     'has_capacity': True,
#     'is_enrollment_open': True
# }
```

## API Endpoints

### Basic CRUD

```bash
# List
GET /api/school-operations/school-years/
GET /api/school-operations/school-years/?school=1&status=active

# Create
POST /api/school-operations/school-years/
{
    "school": 1,
    "academic_year": 1,
    "use_guinea_defaults": true,
    "capacity": 500
}

# Retrieve
GET /api/school-operations/school-years/1/

# Update
PATCH /api/school-operations/school-years/1/
{
    "capacity": 600
}

# Delete (soft)
DELETE /api/school-operations/school-years/1/
```

### Custom Actions

```bash
# Activate
POST /api/school-operations/school-years/1/activate/

# Complete
POST /api/school-operations/school-years/1/complete/

# Archive
POST /api/school-operations/school-years/1/archive/

# Add holiday
POST /api/school-operations/school-years/1/add-holiday/
{
    "name": "Christmas Break",
    "start_date": "2024-12-20",
    "end_date": "2025-01-05"
}

# Update setting
POST /api/school-operations/school-years/1/update-setting/
{
    "key": "assessment.passing_grade",
    "value": 12.0
}

# Get statistics
GET /api/school-operations/school-years/1/statistics/
```

### Filters

```bash
# Current years
GET /api/school-operations/school-years/current/
GET /api/school-operations/school-years/current/?school=1

# Active years
GET /api/school-operations/school-years/active/

# Open enrollment
GET /api/school-operations/school-years/open-enrollment/

# By school
GET /api/school-operations/school-years/by-school/1/
GET /api/school-operations/school-years/by-school/1/?include_archived=true

# By academic year
GET /api/school-operations/school-years/by-academic-year/1/
```

## Status Values

```python
SchoolYearStatus.PLANNING    # 'planning'
SchoolYearStatus.ACTIVE      # 'active'
SchoolYearStatus.COMPLETED   # 'completed'
SchoolYearStatus.ARCHIVED    # 'archived'
```

## Key Constraints

- ✅ One school year per school per academic year
- ✅ One current year per school
- ✅ One active year per school
- ✅ Unique date ranges per school (no overlap)
- ✅ End date > Start date
- ✅ Enrollment end ≤ Year start
- ✅ Capacity ≤ School capacity
- ✅ Enrollment count ≤ Capacity

## Default Settings Structure

```python
{
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
```

## Admin Interface

### URL
`/admin/school_operations/schoolyear/`

### Key Features
- Color-coded status badges
- Enrollment progress bars
- Capacity indicators
- Current year markers (✓)
- Bulk actions (activate, complete, archive)
- Advanced filtering
- Search by name, code, description

## Testing

```bash
# Run all tests
python -m pytest domain/school_operations/tests/test_school_year.py -v

# Run specific test class
python -m pytest domain/school_operations/tests/test_school_year.py::TestSchoolYearModel -v

# Run with coverage
python -m pytest domain/school_operations/tests/test_school_year.py --cov=domain.school_operations.models.school_year
```

## Troubleshooting

### Common Issues

**Issue**: ValidationError on save
```python
# Solution: Check business rules
school_year.full_clean()  # See specific validation errors
```

**Issue**: Cannot activate year
```python
# Check: Only one active year per school
active = SchoolYearSelector.get_active_for_school(school)
if active:
    active.complete(user=user)  # Complete existing first
school_year.activate(user=user)
```

**Issue**: Capacity exceeded
```python
# Check available capacity
if school_year.has_capacity():
    school_year.increment_enrollment_count(1)
else:
    print(f"Full! Capacity: {school_year.capacity}")
```

**Issue**: Enrollment closed
```python
# Check dates
print(f"Period: {school_year.enrollment_start_date} to {school_year.enrollment_end_date}")
print(f"Is open: {school_year.is_enrollment_open()}")
```

## Performance Tips

1. **Use select_related** for queries:
```python
SchoolYear.objects.select_related('school', 'academic_year').all()
```

2. **Use bulk operations** for multiple schools:
```python
SchoolYearService.bulk_create_school_years_for_academic_year(
    academic_year=academic_year,
    schools=schools,
    user=request.user
)
```

3. **Cache current/active** years:
```python
# Cache frequently accessed current years
from django.core.cache import cache
cache_key = f'current_school_year_{school.id}'
current = cache.get(cache_key)
if not current:
    current = SchoolYearSelector.get_current_for_school(school)
    cache.set(cache_key, current, 3600)  # 1 hour
```

## Related Models

- **School**: `domain.school_operations.models.School`
- **AcademicYear**: `domain.academic.models.AcademicYear`
- **User**: `domain.account.models.User` (audit trail)

## Documentation

- **Full Guide**: `SCHOOL_YEAR_IMPLEMENTATION.md`
- **Summary**: `SCHOOL_YEAR_SUMMARY.md`
- **This Card**: `SCHOOL_YEAR_QUICK_REFERENCE.md`

---

**Quick Help**: All operations require a `user` parameter for audit trail.
**Support**: Check tests in `domain/school_operations/tests/test_school_year.py` for examples.
