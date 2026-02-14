# Scheduling/Timetable Domain - Implementation Plan

## 1. Overview

The Scheduling domain manages class timetables (emplois du temps) by organizing when and where teachers teach specific subjects to classrooms.

### Business Purpose
- Create and manage weekly class schedules
- Prevent scheduling conflicts (same teacher/classroom at same time)
- Support schedule versioning (effective_from/effective_to dates)
- Enable queries for teacher workload and student timetables
- Maintain historical schedule data

### Key Principles
- **Read-only consumption**: Schedule consumes existing TeacherAssignments, doesn't create them
- **Conflict prevention**: Automated validation prevents double-booking
- **Historical tracking**: All schedules preserved with validity periods
- **Status workflow**: DRAFT → ACTIVE → SUSPENDED → ARCHIVED

---

## 2. Domain Model

### Schedule Model

```python
class Schedule(AuditModel):
    """
    Represents a single scheduled class session (one time slot, one day).
    
    Business Rules:
        - teacher_assignment must have status ACTIVE
        - No time conflicts for same classroom, teacher, or time_slot
        - effective_from required, effective_to optional
        - status workflow: DRAFT → ACTIVE → SUSPENDED → ARCHIVED
        - Cannot modify ARCHIVED schedules
        
    Relationships:
        - Belongs to: SchoolYear, SchoolYearCycle, Classroom, TeacherAssignment
        - Uses: SchoolYearCycleTimeSlot for timing
    """
    
    # Core relationships
    school_year: FK → SchoolYear
    school_year_cycle: FK → SchoolYearCycle
    classroom: FK → Classroom
    teacher_assignment: FK → TeacherAssignment
    
    # Timing
    day_of_week: CharField (MONDAY, TUESDAY, ..., SUNDAY)
    time_slot: FK → SchoolYearCycleTimeSlot
    
    # Validity period
    effective_from: DateField
    effective_to: DateField (nullable)
    
    # Status
    status: CharField (DRAFT, ACTIVE, SUSPENDED, ARCHIVED)
    
    # Metadata (from AuditModel)
    is_deleted: BooleanField
    created_at, updated_at: DateTimeField
```

### Constants/Enums

```python
class DayOfWeek(models.TextChoices):
    MONDAY = "MONDAY", "Monday"
    TUESDAY = "TUESDAY", "Tuesday"
    WEDNESDAY = "WEDNESDAY", "Wednesday"
    THURSDAY = "THURSDAY", "Thursday"
    FRIDAY = "FRIDAY", "Friday"
    SATURDAY = "SATURDAY", "Saturday"
    SUNDAY = "SUNDAY", "Sunday"

class ScheduleStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"              # Being prepared
    ACTIVE = "ACTIVE", "Active"           # Currently in use
    SUSPENDED = "SUSPENDED", "Suspended"  # Temporarily disabled
    ARCHIVED = "ARCHIVED", "Archived"     # Historical record
```

---

## 3. Business Rules & Constraints

### Database Constraints

1. **Unique Active Schedule per Slot**
   - No duplicate ACTIVE schedules for same (classroom, day_of_week, time_slot, effective period)
   
2. **Teacher Conflict Prevention**
   - Same teacher cannot be scheduled in different classrooms at same (day_of_week, time_slot, effective period)
   
3. **Time Slot Validity**
   - time_slot must belong to the school_year_cycle
   
4. **Date Coherence**
   - effective_from < effective_to (if effective_to is set)
   - effective_from must be within school_year period
   
5. **Teacher Assignment Status**
   - teacher_assignment must have status ACTIVE

### Model Validation (clean method)

```python
def clean(self):
    # 1. Validate teacher_assignment is ACTIVE
    if self.teacher_assignment.assignment_status != TeacherAssignmentStatus.ACTIVE:
        raise ValidationError("Only ACTIVE teacher assignments can be scheduled")
    
    # 2. Validate time_slot belongs to school_year_cycle
    if self.time_slot.school_year_cycle_id != self.school_year_cycle_id:
        raise ValidationError("Time slot must belong to the school year cycle")
    
    # 3. Validate classroom matches teacher_assignment
    if self.classroom_id != self.teacher_assignment.classroom_id:
        raise ValidationError("Classroom must match teacher assignment")
    
    # 4. Validate school_year_cycle matches classroom
    if self.school_year_cycle_id != self.classroom.school_year_level.school_year_cycle_id:
        raise ValidationError("School year cycle must match classroom's cycle")
    
    # 5. Validate effective dates
    if self.effective_to and self.effective_from >= self.effective_to:
        raise ValidationError("effective_to must be after effective_from")
    
    # 6. Validate effective_from within school year
    school_year = self.school_year
    if self.effective_from < school_year.start_date or self.effective_from > school_year.end_date:
        raise ValidationError("effective_from must be within school year period")
```

### Service-Level Validation

```python
# Conflict detection (in ScheduleService.create)
- Check classroom conflicts (same classroom, day, time_slot, overlapping period)
- Check teacher conflicts (same teacher, day, time_slot, overlapping period)
- Raise ConflictError with details if conflicts found
```

---

## 4. Services Layer

### ScheduleService

```python
class ScheduleService:
    @staticmethod
    def create(*, data: dict) -> Schedule:
        """Create new schedule with conflict validation"""
        # 1. Validate teacher_assignment is ACTIVE
        # 2. Check for classroom conflicts
        # 3. Check for teacher conflicts
        # 4. Create schedule
        # 5. Return schedule
    
    @staticmethod
    def update(*, schedule_id: int, data: dict) -> Schedule:
        """Update schedule (not allowed if ARCHIVED)"""
        # 1. Fetch schedule
        # 2. Validate not ARCHIVED
        # 3. Run conflict checks if timing changed
        # 4. Update and save
        # 5. Return schedule
    
    @staticmethod
    def delete(*, schedule_id: int) -> None:
        """Soft delete schedule"""
        # 1. Fetch schedule
        # 2. Validate can delete (business rules)
        # 3. Soft delete
    
    @staticmethod
    def change_status(*, schedule_id: int, new_status: str) -> Schedule:
        """Change schedule status with validation"""
        # 1. Fetch schedule
        # 2. Validate status transition
        # 3. Update status
        # 4. Return schedule
    
    @staticmethod
    def detect_conflicts(*, schedule_data: dict) -> dict:
        """Check for conflicts without creating schedule"""
        # Return: {
        #   "has_conflicts": bool,
        #   "classroom_conflicts": [...],
        #   "teacher_conflicts": [...]
        # }
    
    @staticmethod
    def bulk_create(*, schedules_data: list) -> dict:
        """Create multiple schedules with validation"""
        # Return: {
        #   "created": [...],
        #   "failed": [{schedule_data, errors}, ...]
        # }
```

---

## 5. Selectors Layer

### ScheduleSelector

```python
class ScheduleSelector:
    @staticmethod
    def get_all(*, school_year_id: int = None, status: str = None) -> QuerySet:
        """List all schedules with filters"""
    
    @staticmethod
    def get_by_id(*, schedule_id: int) -> Schedule:
        """Get single schedule by ID"""
    
    @staticmethod
    def get_by_classroom(*, classroom_id: int, day_of_week: str = None, 
                         effective_date: date = None) -> QuerySet:
        """Get classroom timetable"""
    
    @staticmethod
    def get_by_teacher(*, teacher_id: int, day_of_week: str = None,
                       effective_date: date = None) -> QuerySet:
        """Get teacher schedule"""
    
    @staticmethod
    def get_by_student(*, student_id: int, effective_date: date = None) -> QuerySet:
        """Get student timetable (via enrollment)"""
    
    @staticmethod
    def get_active_schedules(*, school_year_id: int, effective_date: date) -> QuerySet:
        """Get all active schedules for a date"""
    
    @staticmethod
    def get_conflicts(*, classroom_id: int = None, teacher_id: int = None,
                      day_of_week: str, time_slot_id: int,
                      effective_from: date, effective_to: date = None) -> QuerySet:
        """Find scheduling conflicts"""
```

---

## 6. API Layer

### Serializers

```python
class ScheduleSerializer(serializers.ModelSerializer):
    # Include nested read fields
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='teacher_assignment.subject.name', read_only=True)
    time_slot_display = serializers.CharField(source='time_slot.__str__', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'school_year', 'school_year_cycle', 'classroom',
            'teacher_assignment', 'day_of_week', 'time_slot',
            'effective_from', 'effective_to', 'status',
            'classroom_name', 'teacher_name', 'subject_name', 'time_slot_display',
            'created_at', 'updated_at'
        ]

class ScheduleDetailSerializer(serializers.ModelSerializer):
    # More detailed with full nested objects
    
class TimetableSerializer(serializers.Serializer):
    # Formatted for display (grouped by day/time)
    day_of_week = serializers.CharField()
    time_slots = serializers.ListField()
    # Each time_slot contains: time_slot_info, subject, teacher, classroom
```

### ViewSets/Views

```python
class ScheduleViewSet(ModelViewSet):
    """CRUD operations for schedules"""
    permission_classes = [IsSchoolStaffOrAdmin]
    
    # GET /api/scheduling/schedules/
    # POST /api/scheduling/schedules/
    # GET /api/scheduling/schedules/{id}/
    # PUT/PATCH /api/scheduling/schedules/{id}/
    # DELETE /api/scheduling/schedules/{id}/

class ScheduleConflictCheckView(APIView):
    """Check for conflicts before creating"""
    # POST /api/scheduling/schedules/check-conflicts/

class ClassroomTimetableView(APIView):
    """Get timetable for a classroom"""
    # GET /api/scheduling/timetables/classroom/{id}/

class TeacherScheduleView(APIView):
    """Get schedule for a teacher"""
    # GET /api/scheduling/timetables/teacher/{id}/

class StudentTimetableView(APIView):
    """Get timetable for a student"""
    # GET /api/scheduling/timetables/student/{id}/

class BulkScheduleCreateView(APIView):
    """Create multiple schedules at once"""
    # POST /api/scheduling/schedules/bulk-create/
```

### URL Routing

```python
# domain/scheduling/api/urls.py
router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('schedules/check-conflicts/', ScheduleConflictCheckView.as_view()),
    path('schedules/bulk-create/', BulkScheduleCreateView.as_view()),
    path('timetables/classroom/<int:classroom_id>/', ClassroomTimetableView.as_view()),
    path('timetables/teacher/<int:teacher_id>/', TeacherScheduleView.as_view()),
    path('timetables/student/<int:student_id>/', StudentTimetableView.as_view()),
]
```

---

## 7. Testing Strategy

### Model Tests
- Test model creation with valid data
- Test all validation rules
- Test constraints (uniqueness, conflicts)
- Test status property methods

### Service Tests
- Test create with conflict detection
- Test update with validation
- Test delete (soft delete)
- Test status changes
- Test bulk_create
- Test conflict detection utility

### Selector Tests
- Test get_by_classroom
- Test get_by_teacher
- Test get_by_student
- Test get_conflicts
- Test filtering by status, date

### API Tests
- Test CRUD endpoints (permissions, validation)
- Test conflict check endpoint
- Test timetable retrieval endpoints
- Test bulk create endpoint
- Test error responses

### Integration Tests
- Test complete workflow: create teacher assignment → create schedule
- Test conflict scenarios (same teacher, same classroom)
- Test timetable generation for student

---

## 8. Implementation Checklist

### Phase 1: Foundation (Models & Constants)
- [ ] Create `domain/scheduling/` directory structure
- [ ] Create `constants.py` with DayOfWeek and ScheduleStatus
- [ ] Create `models/schedule.py` with full validation
- [ ] Create `models/__init__.py`
- [ ] Update domain `__init__.py` to include scheduling app
- [ ] Create and run migrations
- [ ] Add to admin.py

### Phase 2: Business Logic (Services & Selectors)
- [ ] Create `services/schedule.py` with all methods
- [ ] Create `selectors/schedule.py` with all queries
- [ ] Create `services/__init__.py` and `selectors/__init__.py`
- [ ] Add conflict detection logic
- [ ] Add status transition validation

### Phase 3: API Layer
- [ ] Create `api/serializers/schedule.py`
- [ ] Create `api/views/schedule.py` with ViewSet
- [ ] Create timetable view classes
- [ ] Create conflict check view
- [ ] Create bulk create view
- [ ] Create `api/urls.py`
- [ ] Add to main config/urls.py

### Phase 4: Testing
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Create `tests/test_models.py`
- [ ] Create `tests/test_services.py`
- [ ] Create `tests/test_selectors.py`
- [ ] Create `tests/test_api.py`
- [ ] Run all tests and verify passing

### Phase 5: Documentation
- [ ] Create `API_USAGE.md` with examples
- [ ] Create `README.md` for scheduling domain
- [ ] Add inline code documentation
- [ ] Update main project README

---

## 9. Dependencies & Integration Points

### Required Models (Already Exist)
- ✅ SchoolYear (school_operations)
- ✅ SchoolYearCycle (school_operations)
- ✅ SchoolYearCycleTimeSlot (school_operations)
- ✅ Classroom (enrollment)
- ✅ TeacherAssignment (enrollment)
- ✅ StudentEnrollment (enrollment) - for student timetables

### Future Dependencies (Not in Scope)
- Attendance tracking
- Exam planning
- Room assignment (optional)
- Automatic schedule generation

---

## 10. Example Use Cases

### Use Case 1: Create Weekly Schedule for a Class
```python
# For each day and time slot, create a schedule entry
ScheduleService.create(
    school_year_id=1,
    school_year_cycle_id=1,
    classroom_id=5,
    teacher_assignment_id=10,  # Math teacher for this class
    day_of_week="MONDAY",
    time_slot_id=1,  # 8:00-9:00
    effective_from=date(2024, 9, 1),
    effective_to=None,  # Until further notice
    status="ACTIVE"
)
```

### Use Case 2: Check for Conflicts
```python
conflicts = ScheduleService.detect_conflicts(
    classroom_id=5,
    teacher_id=20,
    day_of_week="MONDAY",
    time_slot_id=1,
    effective_from=date(2024, 9, 1)
)
# Returns: {"has_conflicts": True, "classroom_conflicts": [...], "teacher_conflicts": [...]}
```

### Use Case 3: Get Student Timetable
```python
# Student enrolled in classroom_id=5
timetable = ScheduleSelector.get_by_student(
    student_id=100,
    effective_date=date(2024, 9, 15)
)
# Returns all scheduled classes for the student's classroom
```

### Use Case 4: Get Teacher Workload
```python
schedule = ScheduleSelector.get_by_teacher(
    teacher_id=20,
    effective_date=date(2024, 9, 15)
)
# Returns all scheduled classes for this teacher
# Can aggregate to calculate hours per week
```

---

## 11. Non-Functional Requirements

### Performance
- Index on (classroom, day_of_week, time_slot) for fast conflict detection
- Index on (teacher_assignment, day_of_week) for teacher schedules
- Optimize queries with select_related for timetable views

### Security
- Only SCHOOL_ADMIN and STAFF can create/modify schedules
- Teachers can view their own schedules (read-only)
- Students/Parents can view student timetables (read-only)

### Data Integrity
- Soft delete only (preserve historical schedules)
- Audit trail (created_at, updated_at from AuditModel)
- No cascade deletes (PROTECT on all FKs)

---

## 12. Future Enhancements (Out of Scope)

- [ ] Automatic schedule generation algorithm
- [ ] Room assignment and tracking
- [ ] Substitution/replacement tracking
- [ ] Schedule templates
- [ ] Bulk schedule import (CSV/Excel)
- [ ] Schedule versioning (full history)
- [ ] Integration with attendance system
- [ ] Schedule optimization (minimize gaps)
- [ ] Conflict resolution suggestions

---

## 13. Estimated Effort

| Task | Estimated Time |
|------|----------------|
| Models & Constants | 2 hours |
| Services & Selectors | 3 hours |
| API Layer | 3 hours |
| Testing | 3 hours |
| Documentation | 1 hour |
| **Total** | **12 hours** |

---

## 14. Success Criteria

- ✅ All models created with proper validation
- ✅ Conflict detection prevents double-booking
- ✅ All CRUD operations working via API
- ✅ Timetable views functional for classroom, teacher, student
- ✅ All tests passing (>95% coverage)
- ✅ API documentation complete with examples
- ✅ No breaking changes to existing domains

---

**Ready to implement!** 🚀
