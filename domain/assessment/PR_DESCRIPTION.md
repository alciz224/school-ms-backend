# Assessment v1: Bulk grading (preview + commit), optimized selectors, status transitions, and portal-ready endpoints

## Summary
This PR implements the core of the Assessment domain in a portal-friendly, performance-safe way. It introduces class-based bulk grading with anti-N+1 patterns, status transition workflows, optimized read selectors for teacher/admin/student views, and a minimal, meaningful test suite.

## What’s included

### Reporting (ReportCard & Transcript)
- **ReportCard** (persisted, frozen): weighted averages, rank per classroom+term, snapshot in `raw_data`
- **ReportCardSubject** lines: per subject averages with coefficients
- **Transcript**: annual aggregation from report cards
- **Services**:
  - `ReportCardService.generate_for_classroom_term` (bulk, anti-N+1)
  - `TranscriptService.generate_for_student`
- **Reporting endpoints**:
  - `POST /api/v1/assessment/report-cards/generate/`
  - `GET /api/v1/assessment/report-cards/student/{enrollment_id}/term/{term_id}/`
  - `GET /api/v1/assessment/report-cards/classroom/{classroom_id}/term/{term_id}/`
  - `POST /api/v1/assessment/transcripts/generate/`
  - `GET /api/v1/assessment/transcripts/student/{enrollment_id}/year/{school_year_id}/`

### Models and business rules
- **Assessment**: unique per `(school_year_cycle, assessment_type, term)`, dates within term, status transitions (DRAFT → ACTIVE → CLOSED → ARCHIVED)
- **AssessmentSubject**: unique per `(assessment, classroom, school_year_level_subject)`; validates `teacher_assignment` is ACTIVE and coherent; `max_score` at subject level; status transitions (DRAFT → PUBLISHED → CLOSED → ARCHIVED)
- **StudentAssessment**: unique per `(assessment_subject, student_enrollment)`; absence logic (absent ⇒ no score); `0 ≤ score ≤ max_score`; no `normalized_score` (uniform base per level as agreed)

### Services (write) with anti-N+1 bulk pattern
- `StudentAssessmentService.preview_bulk_import`
  - Loads subject, classroom enrollments, existing grades in 3 fixed queries
  - Validates in-memory, returns creates/updates counts and per-item errors
- `StudentAssessmentService.commit_bulk_import`
  - All-or-nothing atomic upsert: update if exists, else create
  - On error: returns structured `ValidationException` with code and details (index, enrollment_id), surfaced by DRF handler as `{ "success": false, "error": { ... } }`
- `AssessmentService` & `AssessmentSubjectService`
  - `activate/close/archive` and `publish/close/archive` transitions with guardrails

### Selectors (read) optimized for portals
- `ClassroomGradingSelector.get_classroom_grading_sheet(assessment_subject_id)` — Roster + existing scores in 2–3 queries, stable ordering
- `AssessmentOverviewSelector.get_assessment_overview(assessment_id)`
- `StudentGradesSelector.get_student_grades_history(student_enrollment_id)`
- `StudentGradesSelector.calculate_classroom_averages(classroom_id)`

### API endpoints (portal-based permissions)
- **Bulk grading**:
  - `POST /api/v1/assessment/assessment-subjects/{id}/grades/preview`
  - `POST /api/v1/assessment/assessment-subjects/{id}/grades/commit`
- **Read (teacher/admin/student)**:
  - `GET /api/v1/assessment/assessments/{id}/overview`
  - `GET /api/v1/assessment/assessment-subjects/{id}/grading-sheet`
  - `GET /api/v1/assessment/students/{enrollment_id}/grades`
  - `GET /api/v1/assessment/classrooms/{id}/averages`
- **Status**:
  - `POST /api/v1/assessment/assessments/{id}/status/{activate|close|archive}`
  - `POST /api/v1/assessment/assessment-subjects/{id}/status/{publish|close|archive}`
- Permissions use session’s `current_role` (TEACHER/STUDENT/STAFF), consistent with the project

### Exception handling (structured error codes)
- **Preview**: each invalid row includes `{ index, enrollment_id, code, detail }`
- **Commit**: raises `ValidationException` with `code` + `details`; DRF wrapper returns `{ "success": false, "error": { code, message, details } }`.
- Frontends can consume machine-readable codes:
  - `not_in_classroom`, `absent_with_score`, `score_required_when_present`, `missing_enrollment_id`, `invalid_score`, `score_exceeds_max`, `negative_score`, `validation_error`

### Tests (business + API + negative)
- **Business**: transitions; bulk preview/commit (all-or-nothing); grading sheet returns roster and scores
- **API**: bulk endpoints happy path (teacher), invalid absent-with-score, teacher-only access to grading sheet; staff-only transitions
- **Negative**: enrollment not in classroom; missing `enrollment_id`; negative score; present without score
- All targeted tests pass

## Implementation notes
- Avoided N+1 issues by preloading assessment subject, enrollments, and existing scores in fixed queries; bulk operations in 1–2 writes
- Removed risky `only()` usage in selectors to prevent DRF/ORM field deferral conflicts; added safe `order_by('id')`
- Kept atomicity: commit rejects the entire batch on first validation error but returns structured error payload for frontend alignment
- Session-based roles enforced via existing portal permission classes

## Why this approach
- **Teacher workflow**: class-based data import with preview + commit mirrors real usage (Excel/CSV/UI) and prevents N+1 bottlenecks
- **Consistency for frontends**: machine-readable error codes for robust UX and import troubleshooting
- **Portal-ready**: endpoints mapped to teacher/admin/student roles with minimal complexity

## Migration notes
- New app `domain.assessment` added; migrations included (indexes and constraints within 30-char limits)

## How to test
- Service tests:
  - `pytest -q domain/assessment/tests/test_business.py`
  - `pytest -q domain/assessment/tests/test_negative.py`
- API smoke:
  - `pytest -q domain/assessment/tests/test_api.py`
  - `pytest -q domain/assessment/tests/test_api_negative.py`

## Future work (next PRs)
- Rate limiting and payload-size checks on bulk endpoints (optional)
- Optional: return per-row structured error list for commit if we want non-atomic behavior (currently all-or-nothing by design)
- API doc snippets and a small importer guide for frontends
