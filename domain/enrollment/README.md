# Enrollment Domain

## Overview

The **Enrollment** domain manages student enrollment and classroom assignment within school years. It is designed for **portal-based applications** where different user roles (school admin, teacher, student, parent) access relevant enrollment data.

---

## Core Concepts

### 1. Classroom
A physical/pedagogical class for a specific `SchoolYearLevel`.

**Key fields:**
- `school_year_level` (FK)
- `name` (e.g., "A", "B1")
- `capacity`
- `room_number`

**Rules:**
- Unique per `(school_year_level, name)` for non-deleted records.

### 2. StudentEnrollment
Represents a student's enrollment in a `SchoolYearLevel`, optionally assigned to a `Classroom`.

**Key fields:**
- `student` (FK to `CustomUser`, **optional** — some students may not have an account)
- `first_name`, `last_name` (snapshot for students without accounts and historical consistency)
- `school_year_level` (FK)
- `classroom` (FK, nullable)
- `previous_classroom` (FK, nullable, for transfer tracking)
- `enrollment_status`: `PRE_REGISTERED`, `ACTIVE`, `COMPLETED`, `DROPPED`
- `annual_identifier` (unique, required)
- `classroom_identifier` (optional)
- `classroom_suffix` (int, optional, auto-calculated for homonyme disambiguation)

**Rules:**
- Unique per `(student, school_year_level)` when `student` is not null.
- `annual_identifier` is globally unique (for non-deleted records).
- If `enrollment_status != PRE_REGISTERED`, `classroom` is required.
- `classroom` must belong to the same `school_year_level`.

### 3. Classroom Suffix (Homonyme Management)
When multiple students with the same `first_name` and `last_name` are in the same classroom, a **suffix** is auto-assigned:

- **Rule A (collision-only):**
  - 1st student with unique name → `classroom_suffix = NULL`
  - When a 2nd student with same name arrives:
    - 1st becomes `suffix=1`
    - 2nd becomes `suffix=2`
  - Further homonymes get `suffix=3`, `4`, etc.

- **Stability:**
  - Suffixes are **stable** (never recalculated downward when a student leaves/transfers).

- **Display:**
  - If suffix is NULL: `"{first_name} {last_name}"`
  - If suffix exists: `"{first_name} {suffix} {last_name}"` (e.g., `Mamadou 1 Diallo`)

---

## Business Workflows

### Create Enrollment
```python
from domain.enrollment.services import StudentEnrollmentService

enrollment = StudentEnrollmentService.create(
    student=user_or_none,
    first_name="Mamadou",
    last_name="Diallo",
    school_year_level=school_year_level,
    enrollment_date=date(2025, 9, 1),
    annual_identifier="SY2025-001",
    classroom=classroom_a,
    enrollment_status="ACTIVE",
    user=admin_user,
)
# classroom_suffix is auto-calculated if collision exists.
```

### Transfer Student
```python
from domain.enrollment.services import StudentEnrollmentService

transferred = StudentEnrollmentService.transfer(
    obj=enrollment,
    to_classroom=classroom_b,
    transfer_date=date(2025, 10, 1),
    transfer_reason="Administrative",
    user=admin_user,
)
# previous_classroom is set; classroom_suffix recalculated in destination classroom.
```

---

## API Endpoints

### Admin/Staff Endpoints (CRUD)
**Permissions:** `SCHOOL_ADMIN` or `STAFF` role in session.

- `GET /api/v1/enrollment/classrooms/` — list classrooms
- `POST /api/v1/enrollment/classrooms/` — create classroom
- `GET /api/v1/enrollment/classrooms/{id}/` — classroom detail
- `PATCH /api/v1/enrollment/classrooms/{id}/` — update classroom
- `DELETE /api/v1/enrollment/classrooms/{id}/` — soft delete classroom

- `GET /api/v1/enrollment/student-enrollments/` — list enrollments
- `POST /api/v1/enrollment/student-enrollments/` — create enrollment
- `GET /api/v1/enrollment/student-enrollments/{id}/` — enrollment detail
- `PATCH /api/v1/enrollment/student-enrollments/{id}/` — update enrollment
- `DELETE /api/v1/enrollment/student-enrollments/{id}/` — soft delete enrollment
- `POST /api/v1/enrollment/student-enrollments/{id}/transfer/` — transfer to another classroom

### Portal-Oriented Roster Endpoints

#### School Admin/Staff
**Permissions:** `SCHOOL_ADMIN` or `STAFF`.

- `GET /api/v1/enrollment/roster/classrooms/` — list classrooms with stats
- `GET /api/v1/enrollment/roster/classrooms/{id}/` — classroom detail with stats
- `GET /api/v1/enrollment/roster/classrooms/{id}/students/` — roster (list of students) for a classroom
- `GET /api/v1/enrollment/roster/classrooms/{id}/stats/` — classroom stats (student count, capacity remaining)
- `GET /api/v1/enrollment/roster/school-year-levels/{id}/enrollments/` — all enrollments for a school year level

#### Teacher Portal
**Permissions:** `TEACHER` role.

- `GET /api/v1/enrollment/roster/my-classes/` — classrooms assigned to the current teacher (TODO: requires TeacherAssignment)

#### Student Portal
**Permissions:** `STUDENT` role.

- `GET /api/v1/enrollment/roster/me/` — current student's enrollments

#### Parent Portal
**Permissions:** `PARENT` role.

- `GET /api/v1/enrollment/roster/my-children/` — enrollments for parent's children (TODO: requires parent-child relationship)

---

## Permissions (Portal-Based)

Since `current_role` is stored in **session** (not on the User model), permissions read from `request.session.get('current_role')`.

### Available Permission Classes

- `HasPortalRole` — flexible permission that checks `view.required_roles`
- `IsSchoolStaffOrAdmin` — allows `SCHOOL_ADMIN` or `STAFF`
- `IsTeacher` — allows `TEACHER`
- `IsStudent` — allows `STUDENT`
- `IsParent` — allows `PARENT`

**Usage example:**
```python
class MyView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]
    ...
```

---

## Models

### Classroom
- **DB Table:** `classroom`
- **Soft Delete:** Yes
- **Audit:** Yes (via `AuditModel`)

### StudentEnrollment
- **DB Table:** `student_enrollment`
- **Soft Delete:** Yes
- **Audit:** Yes (via `AuditModel`)
- **Identifiers:** `annual_identifier` (unique), `classroom_identifier` (optional)
- **Suffix:** `classroom_suffix` (auto-calculated)

---

## Services & Selectors

### Services (Write Operations)
Located in `domain/enrollment/services/`

- `ClassroomService.create/update/delete`
- `StudentEnrollmentService.create/update/transfer`

### Selectors (Read Operations)
Located in `domain/enrollment/selectors/`

- `ClassroomSelector.list/get`
- `StudentEnrollmentSelector.list/get`
- `RosterSelector` (portal-oriented queries):
  - `get_classroom_roster(classroom_id)`
  - `get_school_year_level_enrollments(school_year_level_id)`
  - `get_classroom_with_stats(classroom_id)`
  - `get_student_enrollments(student_id)`

---

## Testing

Run enrollment tests:
```bash
pytest domain/enrollment/tests --maxfail=1
```

Key test files:
- `test_models.py` — model validation and constraints
- `test_services.py` — business logic (create/transfer)
- `test_suffix.py` — homonyme suffix calculation
- `test_permissions.py` — portal-based permissions
- `test_roster_selectors.py` — roster queries

---

## TODO / Future Enhancements

- [ ] Implement `TeacherAssignment` model and link to `Classroom`/`Subject`
- [ ] Implement parent-child relationship for `MyChildrenEnrollmentsView`
- [ ] Auto-generate `annual_identifier` based on school policy
- [ ] Capacity validation (prevent over-enrollment)
- [ ] Bulk enrollment operations (import from CSV)
- [ ] Enrollment history/audit table for full timeline tracking

---

## Domain Dependencies

- `domain.account` (CustomUser)
- `domain.school_operations` (SchoolYearLevel)
- `domain.shared` (AuditModel, exceptions, API utilities)

---

## API Contract Examples

### Create Enrollment (SCHOOL_ADMIN/STAFF)
```http
POST /api/v1/enrollment/student-enrollments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Mamadou",
  "last_name": "Diallo",
  "school_year_level": 12,
  "classroom": 5,
  "enrollment_date": "2025-09-01",
  "annual_identifier": "SY2025-001",
  "enrollment_status": "ACTIVE"
}
```

**Response:**
```json
{
  "id": 1,
  "display_name": "Mamadou Diallo",
  "first_name": "Mamadou",
  "last_name": "Diallo",
  "classroom_suffix": null,
  "student": null,
  "school_year_level": 12,
  "classroom": 5,
  "enrollment_status": "ACTIVE",
  "annual_identifier": "SY2025-001",
  "classroom_identifier": null,
  ...
}
```

### Get Classroom Roster (SCHOOL_ADMIN/STAFF/TEACHER)
```http
GET /api/v1/enrollment/roster/classrooms/5/students/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "display_name": "Mamadou Diallo",
    "first_name": "Mamadou",
    "last_name": "Diallo",
    "classroom_suffix": null,
    "student": null,
    "student_email": null,
    "enrollment_status": "ACTIVE",
    "annual_identifier": "SY2025-001",
    "classroom_identifier": null
  },
  {
    "id": 2,
    "display_name": "Mamadou 1 Diallo",
    "first_name": "Mamadou",
    "last_name": "Diallo",
    "classroom_suffix": 1,
    ...
  }
]
```

---

## Summary

The Enrollment domain is **portal-ready**, with session-based permissions and roster endpoints designed for multi-role access. It handles student enrollment, classroom assignment, transfer workflows, and automatic homonyme disambiguation via suffixes—all while supporting students without platform accounts.
