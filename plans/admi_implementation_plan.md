# Portal Views Implementation Plan

## Overview

The frontend TanStack Start app is already calling session-authenticated endpoints (forwarding `sessionid` + `csrftoken` cookies). The goal is to build **dedicated DRF views inside `portal/system_admin` and `portal/school_admin`** that are wired to new URL prefixes, so the frontend adapters can point to clean portal-scoped routes instead of raw domain routes.

---

## What the Frontend Actually Calls (source of truth)

| Frontend Adapter | Base URL | Key Endpoints |
|---|---|---|
| `ApiUsersAdapter` | `/api/v1` | `GET/POST /admin/users/`, `GET/PATCH/DELETE /admin/users/{id}/` |
| `ApiSchoolsAdapter` | `/api/v1` | `GET/POST /school-operations/schools/`, `GET/PATCH/DELETE /school-operations/schools/{id}/`, `GET /school-operations/school-years/by-school/{id}/`, `GET /school-operations/school-year-cycles/by-school-year/{id}/`, `GET /school-operations/school-year-levels/by-school-year-cycle/{id}/`, `GET /school-operations/school-year-level-subjects/?school_year_level={id}`, `GET /enrollment/classrooms/?school_year_level={id}`, `POST /enrollment/classrooms/` |
| `ApiAcademicAdapter` | `/api/v1` | Full CRUD on `/academic/cycles/`, `/academic/levels/`, `/academic/tracks/`, `/academic/subjects/`, `/academic/term-types/`, `/academic/terms/`, `/academic/assessment-types/` |
| `ApiGeographyAdapter` | `/api/v1` | Full CRUD on `/countries/`, `/regions/`, `/administrative-units/`, `/localities/` |
| `ApiTeachersAdapter` | **`/api/v2`** | `GET /teachers/`, `GET /school-years/{id}/teachers/`, `GET /school-year-teachers/{id}/assignments/`, `POST /school-year-teachers/`, `PATCH /school-year-teachers/{id}/`, `POST /teacher-assignments/`, `PATCH /teacher-assignments/{id}/` |
| `ApiStudentsAdapter` | `/api/v1` | `GET /school-admin/students/` with filters, `GET /school-admin/students/{id}/` |
| `ApiParentsAdapter` | `/api/v1` | `GET /school-admin/parents/` with filters, `GET /school-admin/parents/{id}/` |

---

## Key Observations

> [!IMPORTANT]
> **`/api/v1/admin/users/`** already exists and is implemented (`AdminUserViewSet`). The only fix needed is removing the explicit `authentication_classes = [JWTAuthentication]` override so the default `SessionAuthentication` (configured in `settings.py`) kicks in. This is **one line change**.

> [!IMPORTANT]
> **`/api/v1/school-operations/` and `/api/v1/academic/` and geography** are already implemented and wired. The only issue is the `SchoolSerializer` exposes `locality` (FK int) instead of `locality_id` — a small contract fix.

> [!IMPORTANT]
> **`/api/v1/school-admin/students/` and `/api/v1/school-admin/parents/`** do **not exist** yet. These are the primary new portal endpoints needed.

> [!IMPORTANT]
> **`/api/v2/teachers/`** does not exist yet. The teachers adapter points to `/api/v2` for session auth. This needs a new URL prefix + views.

> [!NOTE]
> `school_operations/school-years/by-school/{id}/`, `school-year-cycles/by-school-year/{id}/`, and `school-year-levels/by-school-year-cycle/{id}/` are filter-style custom actions. We need to verify these `@action` methods already exist or add them.

---

## Proposed Changes

### 1. Fix Existing Admin Users Endpoint (1-line)

#### [MODIFY] [`admin_user.py`](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/domain/account/api/views/admin_user.py)
- Remove the explicit `authentication_classes = [JWTAuthentication]` — let settings default (`JWT + Session`) apply.

---

### 2. Fix School Serializer Contract

#### [MODIFY] [`school.py` serializer](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/domain/school_operations/api/serializers/school.py)
- Rename field `locality` → `locality_id` to match the frontend `School` interface.
- Add audit fields: `created_by`, `updated_by`, `is_deleted`, `deleted_at`, `deleted_by`.
- Remove `status` field (not in the frontend `School` type).

---

### 3. Verify/Add School Year & Cycle Custom Actions

#### [MODIFY] [`school_year.py` view](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/domain/school_operations/api/views/school_year.py)
- Ensure `@action(detail=True, url_path='by-school')` or a filter action for `GET /school-years/by-school/{schoolId}/` exists.

#### [MODIFY] [`school_year_cycle.py` view](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/domain/school_operations/api/views/school_year_cycle.py)
- Ensure `GET /school-year-cycles/by-school-year/{schoolYearId}/` action exists.

#### [MODIFY] [`school_year_level.py` view](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/domain/school_operations/api/views/school_year_level.py)
- Ensure `GET /school-year-levels/by-school-year-cycle/{cycleId}/` action exists.

---

### 4. New: `portal/school_admin` — Students & Parents Endpoints

These are the biggest new pieces. The frontend calls `/api/v1/school-admin/students/` and `/api/v1/school-admin/parents/`.

#### [NEW] `portal/school_admin/api/views/students.py`
- `SchoolAdminStudentListView` — `APIView`, `IsSchoolStaffOrAdmin` permission.
- Calls a new `SchoolAdminStudentSelector.list(filters)` that queries `StudentEnrollment` + related models to assemble the `Student` shape expected by the frontend.

#### [NEW] `portal/school_admin/api/views/parents.py`
- `SchoolAdminParentListView` — `APIView`, `IsSchoolStaffOrAdmin` permission.
- Calls a new `SchoolAdminParentSelector.list(filters)` that queries users who have `ParentChild` records and returns the `Parent` shape (with `children_count` and nested `children` array).

#### [NEW] `portal/school_admin/api/serializers/student.py`
- `SchoolAdminStudentSerializer` — matches the frontend `Student` interface exactly (all fields from `students/mocks.ts`).

#### [NEW] `portal/school_admin/api/serializers/parent.py`
- `SchoolAdminParentSerializer` — matches frontend `Parent` interface: `id`, `full_name`, `email`, `phone`, `address`, `children_count`, `children[]`.

#### [NEW] `portal/school_admin/api/selectors/student.py`
- `SchoolAdminStudentSelector.list(*, search, academic_year, cycle, level, class_name, status, gender)` — builds annotated queryset from `StudentEnrollment` with all needed joins.

#### [NEW] `portal/school_admin/api/selectors/parent.py`
- `SchoolAdminParentSelector.list(*, search, has_email, has_phone)`.

#### [NEW] `portal/school_admin/api/urls.py`
```
GET  /api/v1/school-admin/students/       → SchoolAdminStudentListView
GET  /api/v1/school-admin/students/{id}/  → SchoolAdminStudentDetailView
GET  /api/v1/school-admin/parents/        → SchoolAdminParentListView
GET  /api/v1/school-admin/parents/{id}/   → SchoolAdminParentDetailView
```

#### [MODIFY] [`config/urls.py`](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/config/urls.py)
- Add: `path("api/v1/school-admin/", include("portal.school_admin.api.urls", namespace="school_admin"))`

---

### 5. New: `/api/v2/` Teacher Portal Endpoints

The teachers adapter explicitly uses `/api/v2` as base URL.

#### [NEW] `portal/school_admin/api/views/teachers.py`
- `TeacherListView` — `GET /teachers/`
- `SchoolYearTeacherListView` — `GET /school-years/{school_year_id}/teachers/`
- `SchoolYearTeacherAssignmentsView` — `GET /school-year-teachers/{id}/assignments/`
- `SchoolYearTeacherViewSet` — `POST /school-year-teachers/`, `PATCH /school-year-teachers/{id}/`
- `TeacherAssignmentViewSet` — `POST /teacher-assignments/`, `PATCH /teacher-assignments/{id}/`

#### [NEW] `portal/school_admin/api/serializers/teacher.py`
- `TeacherSerializer` — matches `Teacher` interface
- `SchoolYearTeacherSerializer` — matches `SchoolYearTeacher`
- `TeacherAssignmentSerializer` — matches `TeacherAssignment`
- `TeacherClassSerializer` — matches `TeacherClass`

#### [MODIFY] [`config/urls.py`](file:///c:/Users/Daniela/Desktop/school-ms-backend/school-ms-backend/config/urls.py)
- Add: `path("api/v2/", include("portal.school_admin.api.urls_v2", namespace="school_admin_v2"))`

---

## Summary of All New Files

```
portal/school_admin/
  api/
    __init__.py
    urls.py                         (v1 school-admin routes)
    urls_v2.py                      (v2 teacher routes)
    serializers/
      __init__.py
      student.py
      parent.py
      teacher.py
    views/
      __init__.py
      students.py
      parents.py
      teachers.py
    selectors/
      __init__.py
      student.py
      parent.py
```

---

## Verification Plan

### Automated Tests
```powershell
uv run pytest domain/enrollment/tests/ -v
uv run pytest domain/account/tests/ -v
uv run pytest portal/ -v   # after creating tests
```

### Manual Verification
- `GET /api/v1/admin/users/` with a valid session cookie → should return user list (currently fails with 401 due to JWT-only auth)
- `GET /api/v1/school-admin/students/` → returns array matching `Student` interface
- `GET /api/v1/school-admin/parents/` → returns array matching `Parent` interface
- `GET /api/v2/teachers/` → returns array matching `Teacher` interface
