# SchoolYear Model Implementation

## Overview

The SchoolYear model bridges the School and AcademicYear models, managing school-specific academic year operations for Guinea's education system. It handles enrollments, capacity management, and school-year specific configurations.

## Architecture

### Domain-Driven Design Pattern

The implementation follows DDD principles with clear separation of concerns:

```
domain/school_operations/
├── models/
│   └── school_year.py          # Domain model with business logic
├── services/
│   └── school_year.py          # Business logic orchestration
├── selectors/
│   └── school_year.py          # Query operations
├── validators.py               # Validation logic
├── constants.py                # Domain constants
├── api/
│   ├── serializers/
│   │   └── school_year.py      # API serializers
│   └── views/
│       └── school_year.py      # API views
├── admin.py                    # Django admin interface
└── tests/
    └── test_school_year.py     # Comprehensive tests
```

## Model Structure

### Core Fields

**Relationships:**
- `school` (ForeignKey → School): Associated school
- `academic_year` (ForeignKey → AcademicYear): Academic year reference

**Identification:**
- `name`: Human-readable name (e.g., "Lycée Filima 2024-2025")
- `code`: Auto-generated code (e.g., "LYC-FILIMA-001-2024-2025")

**Dates:**
- `start_date`: School year start (typically October in Guinea)
- `end_date`: School year end (typically June)
- `enrollment_start_date`: Enrollment period start
- `enrollment_end_date`: Enrollment period end

**Capacity:**
- `capacity`: Total capacity for the year
- `current_enrollment_count`: Current enrollments (auto-updated)

**Status:**
- `status`: Workflow status (PLANNING → ACTIVE → COMPLETED → ARCHIVED)
- `is_current`: Boolean flag for current year

**Configuration:**
- `settings`: JSON field for year-specific configuration
- `description`: Optional notes

## Business Rules

### Uniqueness Constraints

1. **One school year per school per academic year**
   - Constraint: `unique_school_academic_year`
   
2. **One current year per school**
   - Constraint: `unique_current_school_year`
   - Automatically managed on save

3. **One active year per school**
   - Constraint: `unique_active_school_year`
   - Automatically managed on save

4. **Unique dates per school**
   - Constraint: `unique_school_year_dates`
   - Prevents overlapping years

### Status Workflow

```
PLANNING → ACTIVE → COMPLETED → ARCHIVED
           ↑         ↓
           └─────────┘ (cannot reverse)
```

**Transitions:**
- `activate()`: PLANNING → ACTIVE
- `complete()`: ACTIVE → COMPLETED
- `archive()`: COMPLETED → ARCHIVED

**Rules:**
- Only ACTIVE years can be marked as current
- ARCHIVED years cannot be modified or set as current
- Active years must be completed before archiving

### Date Validation

1. **School year duration:**
   - Minimum: 180 days (6 months)
   - Maximum: 400 days (~13 months)
   - End date must be after start date

2. **Enrollment period:**
   - Minimum: 7 days (1 week)
   - Maximum: 90 days (~12 weeks)
   - Must end before or at year start

3. **Guinea defaults:**
   - Start: October 1st
   - End: June 30th
   - Enrollment: 4 weeks before start

### Capacity Management

1. **School year capacity cannot exceed school capacity**
2. **Current enrollment count auto-updated**
3. **Thread-safe increment/decrement operations**
4. **Capacity validation on enrollment

## Key Features

### 1. Guinea-Specific Calendar

```python
from domain.school_operations.services.school_year import SchoolYearService

# Create with Guinea defaults (October to June)
school_year = SchoolYearService.create_school_year_for_guinea(
    school=school,
    academic_year=academic_year,
    capacity=500,
    user=request.user
)
```

### 2. Settings Management

The `settings` JSON field supports:

```json
{
    "grading_periods": {
        "use_trimesters": true,
        "use_semesters": false,
        "custom_periods": []
    },
    "holidays": [
        {
            "name": "Christmas Break",
            "start_date": "2024-12-20",
            "end_date": "2025-01-05"
        }
    ],
    "attendance": {
        "minimum_attendance_percentage": 75,
        "track_tardiness": true
    },
    "assessment": {
        "grading_scale": "20_point",
        "passing_grade": 10.0,
        "allow_makeup_exams": true
    },
    "calendar": {
        "class_days_per_week": 5,
        "periods_per_day": 6
    },
    "policies": {
        "allow_late_enrollment": false,
        "late_enrollment_deadline": "2024-11-15"
    }
}
```

**Methods:**
- `get_setting(key, default)`: Get nested setting value
- `update_setting(key, value, user)`: Update setting with validation
- `add_holiday(name, start_date, end_date, user)`: Add holiday period

### 3. Enrollment Management

```python
# Check if enrollment is open
if school_year.is_enrollment_open():
    # Process enrollment
    pass

# Check capacity
if school_year.has_capacity():
    available = school_year.available_capacity()
    print(f"{available} spots available")

# Update enrollment count (thread-safe)
school_year.increment_enrollment_count(1)
school_year.decrement_enrollment_count(1)
```

### 4. Status Transitions

```python
# Activate school year
school_year.activate(user=request.user)

# Complete school year
school_year.complete(user=request.user)

# Archive school year
school_year.archive(user=request.user)
```

## Service Layer

### SchoolYearService

**Creation:**
- `create_school_year()`: Create with explicit dates
- `create_school_year_for_guinea()`: Create with Guinea defaults
- `bulk_create_school_years_for_academic_year()`: Bulk creation

**Updates:**
- `update_school_year()`: Update year details
- `update_school_year_setting()`: Update specific setting
- `add_holiday_to_school_year()`: Add holiday period

**Status Management:**
- `activate_school_year()`
- `complete_school_year()`
- `archive_school_year()`
- `delete_school_year()`: Soft delete with validation

**Analytics:**
- `get_enrollment_statistics()`: Get enrollment stats

## Selector Layer

### SchoolYearSelector

**Basic Queries:**
- `get_by_id(id)`
- `get_by_code(code)`
- `get_current_for_school(school)`
- `get_active_for_school(school)`

**Listing:**
- `list_by_school(school, status, include_archived)`
- `list_by_academic_year(academic_year, status)`
- `list_active()`
- `list_planning()`
- `list_with_open_enrollment()`
- `list_with_available_capacity()`

**Advanced:**
- `search(query, school, academic_year, status)`
- `get_school_year_for_enrollment(school, academic_year)`
- `list_overlapping_years(school, start_date, end_date)`
- `list_requiring_attention()`

**Statistics:**
- `get_statistics_by_academic_year(academic_year)`

## API Endpoints

### REST API

```
GET    /api/school-operations/school-years/           - List school years
POST   /api/school-operations/school-years/           - Create school year
GET    /api/school-operations/school-years/{id}/      - Retrieve details
PUT    /api/school-operations/school-years/{id}/      - Update school year
PATCH  /api/school-operations/school-years/{id}/      - Partial update
DELETE /api/school-operations/school-years/{id}/      - Soft delete

# Custom actions
POST   /api/school-operations/school-years/{id}/activate/      - Activate
POST   /api/school-operations/school-years/{id}/complete/      - Complete
POST   /api/school-operations/school-years/{id}/archive/       - Archive
POST   /api/school-operations/school-years/{id}/add-holiday/   - Add holiday
POST   /api/school-operations/school-years/{id}/update-setting/ - Update setting
GET    /api/school-operations/school-years/{id}/statistics/    - Get statistics

# Filters
GET    /api/school-operations/school-years/current/           - Current years
GET    /api/school-operations/school-years/active/            - Active years
GET    /api/school-operations/school-years/open-enrollment/   - Open enrollment
GET    /api/school-operations/school-years/by-school/{id}/    - By school
GET    /api/school-operations/school-years/by-academic-year/{id}/ - By academic year
```

### Query Parameters

- `school`: Filter by school ID
- `academic_year`: Filter by academic year ID
- `status`: Filter by status (planning, active, completed, archived)
- `is_current`: Filter by current flag (true/false)
- `search`: Search by name, code, or description
- `include_archived`: Include archived years (default: false)

## Admin Interface

### Features

1. **List View:**
   - Color-coded status badges
   - Enrollment progress bars
   - Capacity indicators
   - Current year indicators

2. **Filters:**
   - Status, academic year, school type
   - Ownership, active status
   - Creation date

3. **Actions:**
   - Bulk activate
   - Bulk complete
   - Bulk archive
   - Soft delete protection

4. **Display Fields:**
   - Rich enrollment period display
   - Visual capacity indicators
   - Enrollment percentage
   - Available capacity

## Validators

### Custom Validators

1. `validate_school_year_dates()`: Date range validation
2. `validate_enrollment_period()`: Enrollment period validation
3. `validate_school_year_capacity()`: Capacity validation
4. `validate_school_year_settings()`: Settings structure validation

## Database Indexes

Optimized for common queries:

```sql
-- Status queries
CREATE INDEX school_year_status_idx ON school_year (status);

-- School-specific queries
CREATE INDEX school_year_school_status_idx ON school_year (school_id, status);
CREATE INDEX school_year_school_current_idx ON school_year (school_id, is_current);
CREATE INDEX school_year_school_start_idx ON school_year (school_id, start_date);

-- Academic year queries
CREATE INDEX school_year_academic_year_idx ON school_year (academic_year_id);

-- Date range queries
CREATE INDEX school_year_period_idx ON school_year (start_date, end_date);
```

## Testing

### Test Coverage

- **36 comprehensive tests** covering:
  - Model creation and validation
  - Uniqueness constraints
  - Date validations
  - Status workflow
  - Capacity management
  - Settings management
  - Manager methods
  - Business logic

### Running Tests

```bash
# All SchoolYear tests
python -m pytest domain/school_operations/tests/test_school_year.py -v

# Specific test class
python -m pytest domain/school_operations/tests/test_school_year.py::TestSchoolYearModel -v

# Coverage report
python -m pytest domain/school_operations/tests/test_school_year.py --cov=domain.school_operations.models.school_year
```

## Usage Examples

### Creating a School Year

```python
from domain.school_operations.services.school_year import SchoolYearService

# With Guinea defaults
school_year = SchoolYearService.create_school_year_for_guinea(
    school=school,
    academic_year=academic_year,
    capacity=500,
    custom_settings={'grading_periods': {'use_trimesters': True}},
    user=request.user
)

# With explicit dates
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

### Managing School Year Lifecycle

```python
from domain.school_operations.selectors.school_year import SchoolYearSelector
from domain.school_operations.services.school_year import SchoolYearService

# Get current school year for a school
current = SchoolYearSelector.get_current_for_school(school)

# Activate a school year
SchoolYearService.activate_school_year(school_year, user=request.user)

# Add holiday
SchoolYearService.add_holiday_to_school_year(
    school_year=school_year,
    name='Christmas Break',
    start_date=date(2024, 12, 20),
    end_date=date(2025, 1, 5),
    user=request.user
)

# Get statistics
stats = SchoolYearService.get_enrollment_statistics(school_year)
print(f"Enrollment: {stats['enrollment_percentage']}%")
print(f"Available: {stats['available_capacity']} spots")
```

### Querying School Years

```python
from domain.school_operations.selectors.school_year import SchoolYearSelector

# Get all active school years
active_years = SchoolYearSelector.list_active()

# Get years with open enrollment
open_enrollment = SchoolYearSelector.list_with_open_enrollment()

# Search
results = SchoolYearSelector.search(
    query='Lycée',
    status=SchoolYearStatus.ACTIVE,
    academic_year=academic_year
)

# Get year for enrollment
school_year = SchoolYearSelector.get_school_year_for_enrollment(
    school=school,
    academic_year=academic_year
)
```

## Integration Points

### Future Integration

The SchoolYear model is designed to integrate with:

1. **StudentEnrollment**: Enrollment management per school year
2. **Classroom**: Class organization per school year
3. **TeacherAssignment**: Teacher assignments per school year
4. **Assessment**: Evaluations within a school year
5. **Attendance**: Attendance tracking per school year

### Related Domains

- **domain.academic**: AcademicYear, Term, TermType, Cycle, Level
- **domain.school_operations**: School
- **domain.account**: User (audit tracking)

## Performance Considerations

1. **Indexes**: Optimized for common query patterns
2. **Select Related**: Pre-fetch relationships in queries
3. **F() Expressions**: Atomic counter updates for enrollment
4. **Soft Delete**: Physical deletion avoided for data integrity
5. **Caching**: Consider caching current/active years

## Migration

Migration file: `domain/school_operations/migrations/0002_schoolyear.py`

```bash
# Apply migration
python manage.py migrate school_operations
```

## Security

1. **Audit Trail**: All changes tracked with user and timestamp
2. **Soft Delete**: Prevents accidental data loss
3. **Validation**: Comprehensive validation at model level
4. **Permissions**: API requires authentication
5. **Settings Validation**: JSON structure validated

## Conclusion

The SchoolYear model provides a robust, scalable foundation for managing school-specific academic years in Guinea's education system. It follows DDD principles, includes comprehensive validation, and integrates seamlessly with the existing domain architecture.

### Key Benefits

✅ **Guinea-Specific**: Built for Guinea's October-June academic calendar
✅ **Validated**: Comprehensive business rule validation
✅ **Flexible**: JSON settings for year-specific configuration
✅ **Audited**: Full audit trail for compliance
✅ **Tested**: 36 comprehensive tests with 100% pass rate
✅ **Scalable**: Optimized queries and indexes
✅ **Integration-Ready**: Designed for future domain integration
