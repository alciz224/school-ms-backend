# Scheduling Domain

The Scheduling domain manages class timetables (emplois du temps) by organizing when and where teachers teach specific subjects to classrooms.

## Overview

This domain provides:
- **Schedule Management**: Create and manage weekly class schedules
- **Conflict Detection**: Prevent double-booking of teachers and classrooms
- **Timetable Views**: Query schedules by classroom, teacher, or student
- **Status Workflow**: DRAFT → ACTIVE → SUSPENDED → ARCHIVED
- **Historical Tracking**: Maintain schedule history with validity periods

## Key Concepts

### Schedule
A Schedule represents a single scheduled class session:
- One time slot (e.g., Monday 8:00-9:00)
- One classroom
- One teacher teaching one subject
- Valid for a specific date range

### Conflict Prevention
The system automatically prevents:
- Same classroom, same time slot = **Classroom conflict**
- Same teacher, same time slot (different classrooms) = **Teacher conflict**

### Status Workflow
```
DRAFT → Create and prepare timetable
  ↓
ACTIVE → Official, visible to all
  ↓
SUSPENDED → Temporarily disabled (e.g., strike)
  ↓
ARCHIVED → Historical record (read-only)
```

## Models

### Schedule
```python
Schedule(
    school_year,           # FK to SchoolYear
    school_year_cycle,     # FK to SchoolYearCycle
    classroom,             # FK to Classroom
    teacher_assignment,    # FK to TeacherAssignment (must be ACTIVE)
    day_of_week,          # MONDAY, TUESDAY, etc.
    time_slot,            # FK to SchoolYearCycleTimeSlot
    effective_from,       # Date when schedule starts
    effective_to,         # Date when schedule ends (optional)
    status,               # DRAFT, ACTIVE, SUSPENDED, ARCHIVED
)
```

## API Endpoints

### CRUD Operations
```
GET    /api/v1/scheduling/schedules/           # List schedules
POST   /api/v1/scheduling/schedules/           # Create schedule
GET    /api/v1/scheduling/schedules/{id}/      # Get schedule details
PATCH  /api/v1/scheduling/schedules/{id}/      # Update schedule
DELETE /api/v1/scheduling/schedules/{id}/      # Delete schedule
POST   /api/v1/scheduling/schedules/{id}/change_status/  # Change status
```

### Bulk Operations
```
POST   /api/v1/scheduling/schedules/bulk-create/        # Create multiple schedules
POST   /api/v1/scheduling/schedules/check-conflicts/    # Check for conflicts
```

### Timetable Views
```
GET    /api/v1/scheduling/timetables/classroom/{id}/    # Classroom timetable
GET    /api/v1/scheduling/timetables/teacher/{id}/      # Teacher schedule
GET    /api/v1/scheduling/timetables/student/{id}/      # Student timetable
```

## Usage Examples

See [API_USAGE.md](API_USAGE.md) for detailed examples.

### Quick Example: Create a Schedule

```python
from domain.scheduling.services import ScheduleService
from domain.scheduling.constants import DayOfWeek, ScheduleStatus

schedule = ScheduleService.create(data={
    'school_year_id': 1,
    'school_year_cycle_id': 1,
    'classroom_id': 5,
    'teacher_assignment_id': 10,
    'day_of_week': DayOfWeek.MONDAY,
    'time_slot_id': 1,
    'effective_from': date(2024, 9, 1),
    'status': ScheduleStatus.ACTIVE,
})
```

## Permissions

- **SCHOOL_ADMIN, STAFF**: Full CRUD access
- **TEACHER**: View own schedule (read-only)
- **STUDENT**: View own timetable (read-only)
- **PARENT**: View child's timetable (read-only)

## Business Rules

1. **Teacher Assignment Must Be Active**: Only ACTIVE teacher assignments can be scheduled
2. **No Classroom Conflicts**: Cannot schedule different teachers in same classroom at same time
3. **No Teacher Conflicts**: Cannot schedule same teacher in different classrooms at same time
4. **Date Validation**: effective_from must be within school year period
5. **Status Transitions**: Must follow allowed workflow (see constants.py)
6. **Archived Immutable**: Cannot modify ARCHIVED schedules

## Testing

Run tests:
```bash
pytest domain/scheduling/tests/
```

## Related Domains

- **School Operations**: Provides SchoolYear, SchoolYearCycle, SchoolYearCycleTimeSlot
- **Enrollment**: Provides Classroom, TeacherAssignment, StudentEnrollment
- **Academic**: Provides Subject (via SchoolYearLevelSubject)

## Future Enhancements

- Automatic schedule generation
- Room assignment tracking
- Schedule templates
- Bulk import/export (CSV/Excel)
- Schedule optimization algorithms
- Substitution tracking
