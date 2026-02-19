# Frontend Plan — Academic Management System (TanStack Start)

> This repository currently contains backend domains and APIs; frontend is being built with **TanStack Start**.  
> This document is the **living frontend roadmap**: pages, UX flows, data needs, API mapping, and a structured TODO list.

---

## 📚 Documentation Navigation

- **FRONTEND_PLAN.md** (this file) - WHAT to build: pages, features, user flows, API endpoints
- **[TANSTACK_START_IMPLEMENTATION.md](./TANSTACK_START_IMPLEMENTATION.md)** - HOW to build: TanStack Start patterns, auth, routing, forms, deployment

---

## 0) Objectives (What the frontend must achieve)

1. Provide secure, role-based portals for:
   - **System Admin** (platform-wide reference data)
   - **School Admin** (school setup + operations)
   - **Teacher** (rosters, grading, assessments)
   - **Student** (grades, report cards, transcript, timetable)
   - **Parent** (children’s schooling info)
2. Cover the domains implemented in backend:
   - Academic (reference master data)
   - Account/Auth (session + JWT auth, profile, verification, security questions)
   - School Operations (schools, school years, cycles, terms, time slots, levels, subjects, teachers)
   - Enrollment (classrooms, student enrollments, teacher assignments, rosters)
   - Scheduling (timetables/schedules)
   - Assessment (grading sheets, bulk grade import, report cards, transcripts)
   - Geography (countries, regions, administrative units, localities)
3. Provide consistent navigation, filtering by school year/cycle/term, and clear workflows for high-stakes actions (publishing grades, generating report cards).

## 1) Sources of truth (workspace)

- URL root routing: `config/urls.py`
- Domain URL configs:
  - `domain/academic/api/urls.py`
  - `domain/account/api/urls.py`, `domain/account/api/urls_v2.py`
  - `domain/school_operations/api/urls.py`
  - `domain/enrollment/api/urls.py`
  - `domain/scheduling/api/urls.py`
  - `domain/assessment/api/urls.py`
  - `domain/geography/api/urls.py`
- API documentation:
  - `API_ENDPOINTS.md` (auth contract; note it uses `/api/auth/*` in prose but backend mounts at `/api/v1/auth/*`)
  - `schema.yml` (OpenAPI; contains additional actions beyond router CRUD)
- Per-domain “frontend usage” docs:
  - `domain/*/API_USAGE.md` (note: `domain/geography/API_USAGE.md` states base `/api/v1/geography/` but actual mounted base is `/api/v1/`; follow `config/urls.py`)

## 2) Authentication & Session Strategy

Backend provides two auth styles. **TanStack Start uses API v2 (session-based)**.

### 2.1 API v2 (Session-based) ✅ **CURRENT IMPLEMENTATION**
- **Base:** `/api/v2/auth/`
- **Auth Method:** Django sessions with HTTP-only cookies + CSRF tokens
- **Backend:** `http://localhost:8000`
- **Frontend:** TanStack Start server functions handle cookie forwarding

#### How It Works
1. **Initial CSRF Request:** `GET /api/v2/auth/csrf/` sets `sessionid` + `csrftoken` cookies
2. **Mutations:** All POST/PATCH/DELETE requests include `X-CSRFToken` header
3. **Cookie Forwarding:** TanStack Start server functions automatically forward cookies
4. **No Client-Side Token Management:** Cookies are HTTP-only, handled server-side

#### Available Endpoints
- `GET /api/v2/auth/csrf/` - Get CSRF token (call before mutations)
- `POST /api/v2/auth/login/` - Login (sets session cookie)
- `POST /api/v2/auth/logout/` - Logout (clears session)
- `POST /api/v2/auth/register/` - Register new account
- `GET /api/v2/auth/status/` - Check session status (for route guards)

#### Django Configuration (Already Configured)
```python
# Session cookies
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True  # No JS access
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 1209600  # 14 days

# CSRF tokens
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False  # Readable by JS for X-CSRFToken header
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"

# CORS (for localhost:3000)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
```

**See:** `auth/v2/API_CONTRACT.md` for complete documentation.

### 2.2 API v1 (JWT-based) - Not Used in TanStack Start
- Mounted at `/api/v1/auth/`
- For mobile apps or stateless clients
- Includes `/me/`, verification, password flows, security questions

## 3) Roles / Personas and what they need

### 3.1 System Admin (platform)
- Manage platform-wide reference data (Academic + Geography)
- Potentially seed and maintain master catalogs used by schools
- Needs dashboards for data quality (e.g., duplicates, inactive records)

### 3.2 School Admin (school operations)
- Create and configure schools and school years
- Define school-year structure: cycles, terms, time slots
- Configure levels and subjects offered in the school year
- Manage staff/teachers attached to school year
- Manage classrooms, enrollments, teacher assignments
- Create schedules/timetables and check conflicts
- Generate report cards and transcripts (staff-level permissions in assessment docs)

### 3.3 Teacher
- View “My classes” roster
- Access grading sheets per assessment subject
- Bulk import grades (preview then commit)
- View classroom averages and assessment overview
- View own timetable

### 3.4 Student
- View own enrollment(s)
- View grades history
- View report cards per term
- View transcript per year
- View timetable

### 3.5 Parent
- View children’s enrollments
- View child’s timetable
- View child’s report cards and transcript

## 4) Global navigation & layout requirements

### 4.1 App shell
- Top bar: current role (if switchable), profile menu, notifications (future)
- Left navigation: role-based modules
- Main area: pages + contextual filters

### 4.2 Mandatory global context selectors
Many endpoints are scoped by school year/cycle/term. Provide persistent selectors:
- **School** (if user associated with multiple)
- **Current school year** (often used; backend has “current/active” endpoints in School Operations)
- **Cycle / Term** (for reporting/assessments)

### 4.3 Navigation patterns
- List → Detail → Edit as consistent pattern across modules
- Deep links include IDs (e.g., `/school-years/:id`, `/classrooms/:id/roster`)
- “Back” behavior preserves filters and pagination

## 5) Core data relationships (frontend mental model)

### 5.1 Academic (master)
- `AcademicYear` is platform reference; schools create `SchoolYear` tied to an academic year
- `Cycle` groups `Level` and may have `Track`
- `TermType` → `Term`

### 5.2 School Operations (school-specific configuration)
- `School` → many `SchoolYear`
- `SchoolYear` → many `SchoolYearCycle`
- `SchoolYearCycle` → many:
  - `SchoolYearCycleTerm` (terms in that cycle)
  - `SchoolYearCycleTimeSlot` (time slots)
  - `SchoolYearLevel` (levels offered)
- `SchoolYearLevel` → many `SchoolYearLevelSubject`
- `SchoolYearTeacher` ties a teacher/user to the school year

### 5.3 Enrollment
- `Classroom` belongs to school year structure
- `StudentEnrollment` ties a student to a school year level/classroom
- `TeacherAssignment` ties teacher to classroom+subject and drives:
  - scheduling (what can be scheduled)
  - assessment grading sheets

### 5.4 Scheduling
- `Schedule` ties day_of_week + time slot + classroom + teacher assignment
- Timetable views exist for classroom/teacher/student

### 5.5 Assessment & reporting
- Teacher uses `grading sheet` for an `assessment_subject`
- Bulk grade entry uses preview/commit workflow
- Report cards are generated (staff) and then read by students/parents
- Transcripts aggregate report cards

## 6) Page inventory (by role) + API endpoints

> Convention: all endpoints listed below are **fully-qualified** paths.

### 6.1 Common (All authenticated roles)

#### A) Auth & Onboarding
- **Login**
  - v2: `GET /api/v2/auth/csrf/`, `POST /api/v2/auth/login/`
  - v1 alt: `POST /api/v1/auth/login/`
  - UX: form validation, error mapping, “remember me” optional; handle locked/unverified accounts.
- **Register** (if enabled for portal)
  - v2: `POST /api/v2/auth/register/`
  - v1 alt: `POST /api/v1/auth/register/`
- **Logout**
  - v2: `POST /api/v2/auth/logout/`
  - v1 alt: `POST /api/v1/auth/logout/`
- **Password reset**
  - `POST /api/v1/auth/password/reset/`
  - `POST /api/v1/auth/password/reset/confirm/`
  - UX: 2-step flow; success messaging without account enumeration.

#### B) Profile & Security
- **My profile**
  - `GET /api/v1/auth/me/`
  - `PATCH /api/v1/auth/me/`
  - `POST /api/v1/auth/me/email/`
  - `POST /api/v1/auth/me/phone/`
- **Verification center**
  - `GET /api/v1/auth/verify/status/`
  - `POST /api/v1/auth/verify/send/`
  - `POST /api/v1/auth/verify/confirm/`
- **Security questions**
  - `GET /api/v1/auth/security-questions/`
  - `GET /api/v1/auth/security-questions/mine/`
  - `POST /api/v1/auth/security-questions/setup/`
  - `POST /api/v1/auth/security-questions/verify/`
  - `DELETE /api/v1/auth/security-questions/{order}/`

#### C) Role-aware landing page (Dashboard)
- Uses:
  - v2: `GET /api/v2/auth/status/` to bootstrap role/session
  - enrollment roster endpoints per role (see below)
  - “current school year” endpoint (School Ops) for admins/staff

---

### 6.2 System Admin Portal

#### A) Academic Reference Data
Pages (each: List + Create + Edit + Detail where meaningful):
- Academic Years
  - `GET/POST /api/v1/academic/academic-years/`
  - `GET/PATCH/DELETE /api/v1/academic/academic-years/{id}/`
  - Actions (from `schema.yml`):
    - `POST /api/v1/academic/academic-years/{id}/activate/`
    - `POST /api/v1/academic/academic-years/{id}/archive/`
    - `POST /api/v1/academic/academic-years/{id}/set_current/`
    - `GET /api/v1/academic/academic-years/current/`
- Cycles
  - `GET/POST /api/v1/academic/cycles/`
  - `GET/PATCH/DELETE /api/v1/academic/cycles/{id}/`
  - Related reads:
    - `GET /api/v1/academic/cycles/{id}/levels/`
    - `GET /api/v1/academic/cycles/{id}/tracks/`
- Tracks
  - `GET/POST /api/v1/academic/tracks/`
  - `GET/PATCH/DELETE /api/v1/academic/tracks/{id}/`
  - Related reads: `GET /api/v1/academic/tracks/{id}/levels/`
- Levels
  - `GET/POST /api/v1/academic/levels/`
  - `GET/PATCH/DELETE /api/v1/academic/levels/{id}/`
- Subjects
  - `GET/POST /api/v1/academic/subjects/`
  - `GET/PATCH/DELETE /api/v1/academic/subjects/{id}/`
- Assessment Types
  - `GET/POST /api/v1/academic/assessment-types/`
  - `GET/PATCH/DELETE /api/v1/academic/assessment-types/{id}/`
- Term Types & Terms
  - `GET/POST /api/v1/academic/term-types/`
  - `GET/PATCH/DELETE /api/v1/academic/term-types/{id}/`
  - `GET /api/v1/academic/term-types/{id}/terms/`
  - `GET/POST /api/v1/academic/terms/`
  - `GET/PATCH/DELETE /api/v1/academic/terms/{id}/`

UX requirements:
- Data tables with search, filtering (status), and safe “archive/activate” confirmations.
- Inline relationship navigation (cycle → levels, term type → terms).

#### B) Geography Reference Data
Pages: Countries, Regions, Administrative Units, Localities (mounted at `/api/v1/` root)
- `GET/POST /api/v1/countries/`, `GET/PATCH/DELETE /api/v1/countries/{id}/`
- `GET/POST /api/v1/regions/`, `GET/PATCH/DELETE /api/v1/regions/{id}/`
- `GET/POST /api/v1/administrative-units/`, `GET/PATCH/DELETE /api/v1/administrative-units/{id}/`
- `GET/POST /api/v1/localities/`, `GET/PATCH/DELETE /api/v1/localities/{id}/`

---

### 6.3 School Admin Portal

#### A) Schools
- Schools list/manage
  - `GET/POST /api/v1/school-operations/schools/`
  - `GET/PATCH/DELETE /api/v1/school-operations/schools/{id}/`

#### B) School Years (setup & lifecycle)
Pages:
- School years list + detail + edit
Endpoints (core + actions from `schema.yml`):
- `GET/POST /api/v1/school-operations/school-years/`
- `GET/PATCH/DELETE /api/v1/school-operations/school-years/{id}/`
- `GET /api/v1/school-operations/school-years/current/`
- `GET /api/v1/school-operations/school-years/active/`
- `GET /api/v1/school-operations/school-years/by-school/{school_id}/`
- `GET /api/v1/school-operations/school-years/by-academic-year/{academic_year_id}/`
- Actions (exact names per schema):
  - `POST /api/v1/school-operations/school-years/{id}/activate/`
  - `POST /api/v1/school-operations/school-years/{id}/archive/`
  - `POST /api/v1/school-operations/school-years/{id}/complete/`
  - `POST /api/v1/school-operations/school-years/{id}/statistics/` (if POST per schema; confirm)
  - `POST /api/v1/school-operations/school-years/{id}/add-holiday/`
  - `POST /api/v1/school-operations/school-years/{id}/update-setting/`
  - `GET/POST /api/v1/school-operations/school-years/open-enrollment/` (workflow page)

UX requirements:
- “Setup wizard” experience for a new school year:
  1) Create school year (choose academic year, start/end dates)
  2) Create cycles
  3) Add terms and time slots
  4) Configure levels and subjects
  5) Add teachers
  6) Open enrollment

#### C) School Year Cycles / Terms / Time Slots
Pages:
- Cycles list, detail
  - `GET/POST /api/v1/school-operations/school-year-cycles/`
  - `GET/PATCH/DELETE /api/v1/school-operations/school-year-cycles/{id}/`
  - `GET /api/v1/school-operations/school-year-cycles/by-school-year/{school_year_id}/`
  - `GET /api/v1/school-operations/school-year-cycles/by-school/{school_id}/`
  - `GET /api/v1/school-operations/school-year-cycles/active/`
  - `GET /api/v1/school-operations/school-year-cycles/active/by-school/{school_id}/`
  - `POST /api/v1/school-operations/school-year-cycles/bulk-create/`
  - `POST /api/v1/school-operations/school-year-cycles/{id}/restore/`
- Cycle terms
  - `GET/POST /api/v1/school-operations/school-year-cycle-terms/`
  - `GET/PATCH/DELETE /api/v1/school-operations/school-year-cycle-terms/{id}/`
- Cycle time slots
  - `GET/POST /api/v1/school-operations/school-year-cycle-time-slots/`
  - `GET/PATCH/DELETE /api/v1/school-operations/school-year-cycle-time-slots/{id}/`

UX requirements:
- Calendar-like term visibility
- Time-slot grid editor (start/end time, label), with validation and bulk add.

#### D) School Year Levels & Subjects
Pages:
- Levels in a cycle
  - `GET/POST /api/v1/school-operations/school-year-levels/`
  - `GET/PATCH/DELETE /api/v1/school-operations/school-year-levels/{id}/`
  - `GET /api/v1/school-operations/school-year-levels/by-school-year-cycle/{school_year_cycle_id}/`
  - `GET /api/v1/school-operations/school-year-levels/by-school-year/{school_year_id}/`
  - `GET /api/v1/school-operations/school-year-levels/by-school/{school_id}/`
  - `GET /api/v1/school-operations/school-year-levels/active/`
  - `GET /api/v1/school-operations/school-year-levels/active/by-school/{school_id}/`
  - `POST /api/v1/school-operations/school-year-levels/bulk-create/`
  - `POST /api/v1/school-operations/school-year-levels/{id}/restore/`
- Subjects per level
  - `GET/POST /api/v1/school-operations/school-year-level-subjects/`
  - `GET/PATCH/DELETE /api/v1/school-operations/school-year-level-subjects/{id}/`

UX requirements:
- “Curriculum builder”: pick from master `academic/subjects` + set coefficient, teacher eligibility.
- Bulk operations (add many subjects to a level).

#### E) School Year Teachers
- `GET/POST /api/v1/school-operations/school-year-teachers/`
- `GET/PATCH/DELETE /api/v1/school-operations/school-year-teachers/{id}/`

UX requirements:
- Teacher directory, assignment status, ability to filter by cycle/level/subject coverage.

#### F) Classrooms, Enrollments, Teacher Assignments
- Classrooms
  - `GET/POST /api/v1/enrollment/classrooms/`
  - `GET/PATCH/DELETE /api/v1/enrollment/classrooms/{id}/`
- Student enrollments
  - `GET/POST /api/v1/enrollment/student-enrollments/`
  - `GET/PATCH/DELETE /api/v1/enrollment/student-enrollments/{id}/`
  - `POST /api/v1/enrollment/student-enrollments/{id}/transfer/`
- Teacher assignments
  - `GET/POST /api/v1/enrollment/teacher-assignments/`
  - `GET/PATCH/DELETE /api/v1/enrollment/teacher-assignments/{id}/`
  - `POST /api/v1/enrollment/teacher-assignments/{id}/end/`
  - `POST /api/v1/enrollment/teacher-assignments/{id}/replace/`
- Roster views (admin/staff)
  - `GET /api/v1/enrollment/roster/classrooms/`
  - `GET /api/v1/enrollment/roster/classrooms/{id}/students/`
  - `GET /api/v1/enrollment/roster/classrooms/{id}/stats/`
  - `GET /api/v1/enrollment/roster/school-year-levels/{school_year_level_id}/enrollments/`

UX requirements:
- Enrollment wizard: search/create student (note: **no user CRUD endpoint exists yet**; needs backend extension or admin-only approach)
- Transfer flow: choose destination classroom/level and effective date; show warnings.
- Teacher assignment flow: pick classroom + level subject + teacher; status changes and history.

#### G) Scheduling (timetables)
From `domain/scheduling/api/urls.py` and `domain/scheduling/README.md`:
- CRUD schedules
  - `GET/POST /api/v1/scheduling/schedules/`
  - `GET/PATCH/DELETE /api/v1/scheduling/schedules/{id}/`
- Conflict detection
  - `POST /api/v1/scheduling/schedules/check-conflicts/`
- Bulk create
  - `POST /api/v1/scheduling/schedules/bulk-create/`
- Timetable views
  - `GET /api/v1/scheduling/timetables/classroom/{classroom_id}/`
  - `GET /api/v1/scheduling/timetables/teacher/{teacher_id}/`
  - `GET /api/v1/scheduling/timetables/student/{student_id}/`

UX requirements:
- Timetable grid (days × time slots)
- Drag/drop or form-based placement
- Pre-flight conflict check before save; show conflict details grouped by teacher/classroom.

#### H) Reporting operations (Staff)
- Report cards
  - `POST /api/v1/assessment/report-cards/generate/` (payload: `{ classroom_id, term_id, force? }`)
  - `GET /api/v1/assessment/report-cards/classroom/{classroom_id}/term/{term_id}/`
  - `GET /api/v1/assessment/report-cards/student/{enrollment_id}/term/{term_id}/`
- Transcripts
  - `POST /api/v1/assessment/transcripts/generate/` (payload: `{ student_enrollment_id, school_year_id }`)
  - `GET /api/v1/assessment/transcripts/student/{enrollment_id}/year/{school_year_id}/`

UX requirements:
- Generation is high-impact: confirmation modal + audit info + progress indicator.
- “Frozen” report cards: display badge and prevent editing.

---

### 6.4 Teacher Portal

#### A) My Classes
- `GET /api/v1/enrollment/roster/my-classes/`
- Drill-down roster:
  - `GET /api/v1/enrollment/roster/classrooms/{id}/students/` (if permitted)

UI:
- Cards/table for assigned classes (classroom, subjects)
- Quick links: timetable, grading, averages, report cards (read only unless staff)

#### B) Grading workflow
Pages:
- Assessment overview
  - `GET /api/v1/assessment/assessments/{assessment_id}/overview/`
- Grading sheet
  - `GET /api/v1/assessment/assessment-subjects/{assessment_subject_id}/grading-sheet/`
- Bulk grade import
  - `POST /api/v1/assessment/assessment-subjects/{assessment_subject_id}/grades/preview/`
  - `POST /api/v1/assessment/assessment-subjects/{assessment_subject_id}/grades/commit/`
- Classroom averages
  - `GET /api/v1/assessment/classrooms/{classroom_id}/averages/`
- Status transitions (publish/close etc.)
  - `POST /api/v1/assessment/assessments/{assessment_id}/status/{action_name}/`
  - `POST /api/v1/assessment/assessment-subjects/{assessment_subject_id}/status/{action_name}/`

UX requirements:
- Preview-first bulk import UX:
  - Show row-level errors and allow corrections before commit
  - Confirm commit and show summary
- Grading sheet table:
  - Frozen columns: student identity
  - Editable score/absent flags (if supported)
  - Autosave optional; otherwise explicit “Save/Commit”

#### C) Teacher timetable
- `GET /api/v1/scheduling/timetables/teacher/{teacher_id}/`

---

### 6.5 Student Portal

#### A) My enrollment(s)
- `GET /api/v1/enrollment/roster/me/`

#### B) Grades history
- `GET /api/v1/assessment/students/{enrollment_id}/grades/`

#### C) Report cards
- `GET /api/v1/assessment/report-cards/student/{enrollment_id}/term/{term_id}/`

#### D) Transcript
- `GET /api/v1/assessment/transcripts/student/{enrollment_id}/year/{school_year_id}/`

#### E) Student timetable
- `GET /api/v1/scheduling/timetables/student/{student_id}/`

UX requirements:
- Read-only, printable views for report cards/transcripts
- Term/year selectors

---

### 6.6 Parent Portal

#### A) My children enrollments
- `GET /api/v1/enrollment/roster/my-children/`

#### B) Child report cards/transcript
- Same read endpoints as student, using child enrollment id:
  - `GET /api/v1/assessment/report-cards/student/{enrollment_id}/term/{term_id}/`
  - `GET /api/v1/assessment/transcripts/student/{enrollment_id}/year/{school_year_id}/`

#### C) Child timetable
- If timetable is student-id based, parent needs mapping from enrollment → student_id.
- Endpoint:
  - `GET /api/v1/scheduling/timetables/student/{student_id}/`

UX requirement:
- Child switcher (top-level selector) persists across pages.

## 7) UI components (shared library requirements)

### 7.1 Data display
- Table component: pagination, server-side filtering/sorting, column visibility, row actions
- Detail panels: key/value + relationship links
- Status badges: DRAFT/ACTIVE/ARCHIVED etc.

### 7.2 Forms
- Form builder patterns with:
  - client-side validation + server error mapping
  - async selects (searchable dropdowns)
  - date/time pickers (school year, time slots)
  - “bulk add” forms (subjects, cycles, levels)

### 7.3 Scheduling grid
- Week grid with time slot rows and day columns
- Conflict visualization (overlapping bookings)

### 7.4 Reporting views
- Printable layout templates:
  - report card
  - transcript
- Export hooks (future): PDF download/print

### 7.5 Feedback & resilience
- Global toast/alert system
- Empty states and skeleton loading
- Standard error pages: 401/403/404

## 8) UX flows (major features)

### 8.1 School year setup wizard (School Admin)
1. Create School → Create School Year
2. Add cycles (bulk create supported)
3. Add cycle terms and time slots
4. Add levels and level subjects (curriculum)
5. Add school year teachers
6. Create classrooms
7. Enroll students
8. Assign teachers to classroom subjects
9. Build schedules + conflict check

### 8.2 Teacher grading flow
1. Teacher opens “My Classes”
2. Select classroom + subject assessment
3. Open grading sheet
4. Enter grades OR upload/import:
   - preview → fix errors → commit
5. Change status (action endpoint) when ready

### 8.3 Report card generation (Staff)
1. Select classroom + term
2. Show readiness checks (e.g., assessment status, missing grades)
3. Generate report cards (force option guarded)
4. View class list and individual report cards

### 8.4 Parent/Student consumption
1. Choose child/enrollment
2. Choose term/year
3. View report card/transcript
4. Print

## 9) Known gaps / backend dependencies affecting frontend scope

- **User management**: backend provides `/me/` and auth flows, but no explicit endpoints to list/create students/teachers/users globally. Enrollment flows that require selecting/creating users may need:
  - additional backend endpoints, or
  - admin-only creation via Django admin, or
  - separate “directory service” API.
- **Scheduling endpoints in OpenAPI**: `schema.yml` did not show `/api/v1/scheduling/*` in a quick grep (though URLs exist in `domain/scheduling/api/urls.py`). Ensure the API schema generation includes Scheduling.
- **School Operations endpoints missing in OpenAPI**: `schema.yml` did not show `/api/v1/school-operations/schools/*` nor `/api/v1/school-operations/school-year-cycle-time-slots/*` in a quick grep, even though they exist in `domain/school_operations/api/urls.py`. Confirm schema generation includes them.
- **Health endpoint**: `API_ENDPOINTS.md` mentions `/api/health/`, but it does not appear in `config/urls.py` currently; confirm before implementing a status check page.

---

## 10) TODO Roadmap (living checklist)

### Legend
- [ ] Not started
- [~] In progress
- [x] Done

### 10.1 Foundations
- [x] Choose frontend stack: **TanStack Start + TypeScript**
- [ ] Define routing & role-based layouts (System Admin / School Admin / Teacher / Student / Parent)
  - Use TanStack Start file-based routing: `app/routes/`
- [x] Define API client strategy: **Session-based v2 auth with CSRF** (working)
  - [ ] Error mapping + retry rules
  - [ ] TanStack Query setup for caching
- [ ] Global state for context selectors (school, current school year, cycle, term)
  - Use TanStack Router search params or context
- [ ] Design system: typography, spacing, colors, status badges

### 10.2 Auth & Account

> **Implementation Details**: See [TANSTACK_START_IMPLEMENTATION.md](./TANSTACK_START_IMPLEMENTATION.md#2-authentication-session-management) for complete auth patterns with session cookies + CSRF tokens.
- [ ] Login (v2) + session bootstrap via `/api/v2/auth/status/`
- [ ] Logout
- [ ] Register (if enabled)
- [ ] Password reset flow (v1 endpoints)
- [ ] Profile page (`/me/`)
- [ ] Verification center
- [ ] Security questions setup + verify

### 10.3 System Admin: Reference Data
- [ ] Academic reference CRUD pages
  - [ ] Academic years (+ activate/archive/set_current/current)
  - [ ] Cycles (+ related levels/tracks)
  - [ ] Tracks (+ related levels)
  - [ ] Levels
  - [ ] Subjects
  - [ ] Assessment types
  - [ ] Term types + Terms
- [ ] Geography reference CRUD pages (mounted at `/api/v1/` root; **not** under `/api/v1/geography/`)
  - [ ] Countries
  - [ ] Regions
  - [ ] Administrative units
  - [ ] Localities

### 10.4 School Admin: School Operations
- [ ] Schools CRUD pages
- [ ] School years list/detail + lifecycle actions (activate/archive/complete/etc.)
- [ ] Setup wizard UX for school-year configuration
- [ ] School year cycles CRUD + bulk-create + active/by-school filters
- [ ] Cycle terms CRUD
- [ ] Cycle time slots CRUD + grid editor
- [ ] School year levels CRUD + bulk-create + filters
- [ ] School year level subjects CRUD + curriculum builder
- [ ] School year teachers CRUD

### 10.5 Enrollment (Admin/Staff)
- [ ] Classrooms CRUD + roster views
- [ ] Student enrollments CRUD + transfer flow
- [ ] Teacher assignments CRUD + end/replace flows
- [ ] Roster dashboards:
  - [ ] Classroom list + stats
  - [ ] Classroom students list
  - [ ] Level enrollments list

### 10.6 Scheduling
- [ ] Schedule CRUD UI
- [ ] Conflict check UI (preflight)
- [ ] Bulk schedule create UI
- [ ] Timetable views:
  - [ ] Classroom timetable
  - [ ] Teacher timetable
  - [ ] Student timetable

### 10.7 Assessment & Reporting
- [ ] Teacher grading:
  - [ ] Assessment overview page
  - [ ] Grading sheet page
  - [ ] Bulk import preview/commit pages/components
  - [ ] Status transition UI
  - [ ] Classroom averages view
- [ ] Staff reporting:
  - [ ] Report cards generation page
  - [ ] Classroom report cards list page
  - [ ] Student report card view (printable)
  - [ ] Transcript generation page
  - [ ] Transcript view (printable)
- [ ] Student/Parent consumption:
  - [ ] Grades history
  - [ ] Report card viewer
  - [ ] Transcript viewer

### 10.8 Cross-cutting
- [ ] Accessibility: keyboard navigation, focus management, contrast
- [ ] Internationalization (if needed): labels, date formats
- [ ] Audit-friendly UI: show timestamps/statuses and “who did what” where available
- [ ] Performance: caching of reference data, list virtualization for large rosters

---

## 11) How to update this plan

When frontend implementation starts, update this file by:
- marking tasks as [~] and [x]
- adding links to UI mockups, tickets, or PRs
- refining endpoint payload expectations once frontend integrates with real responses

