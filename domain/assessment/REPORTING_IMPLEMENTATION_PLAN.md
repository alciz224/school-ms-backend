# Reporting Phase (ReportCard & Transcript) - Implementation Plan

## 🎯 Objective
Implement reporting layer on top of Assessment domain with **persisted** ReportCards and Transcript, aligned with business rules:
- report cards are **frozen** once generated
- transcripts are built from report cards
- ranking per classroom + term
- decisions are manual (optional field)

---

## ✅ Scope

### **Phase 1: Data Models**

1) **ReportCard**
- One per (student_enrollment, school_year_cycle_term)
- Links to classroom and school year
- Fields: overall_average, rank, generated_at, is_final, decision, raw_data
- Constraints:
  - Unique per (student_enrollment, school_year_cycle_term)
  - Cannot be modified if is_final

2) **ReportCardSubject**
- Child rows for each subject on report card
- Fields: subject, coefficient, average, teacher (optional), remark
- Unique per (report_card, school_year_level_subject)

3) **Transcript**
- One per (student_enrollment, school_year)
- Aggregated from ReportCards
- Fields: overall_average, decision, generated_at, raw_data

---

## ✅ Phase 2: Services (Anti-N+1)

1) **ReportCardGenerationService**
- Input: classroom_id + school_year_cycle_term_id
- Preload all enrollments, assessments, and scores with fixed queries
- Compute per-student:
  - subject averages (only VALIDATED, non-absent)
  - weighted overall average
  - class rank (per term)
- Persist ReportCard + ReportCardSubject in bulk
- Mark as `is_final=True`

2) **TranscriptGenerationService**
- Input: student_enrollment_id or classroom_id
- Aggregate all ReportCards in the school year
- Compute annual averages and store Transcript

3) **Locking Rules**
- ReportCard cannot be re-generated if is_final=True (unless force flag)

---

## ✅ Phase 3: Selectors

- `get_report_card(student_enrollment_id, term_id)`
- `get_classroom_report_cards(classroom_id, term_id)`
- `get_transcript(student_enrollment_id)`

---

## ✅ Phase 4: API Endpoints (Portal-ready)

1) **Generate ReportCard** (Staff)
- POST `/api/v1/assessment/report-cards/generate/`
  - payload: { classroom_id, term_id }

2) **Get ReportCard**
- GET `/api/v1/assessment/report-cards/{id}/`
- GET `/api/v1/assessment/report-cards/student/{enrollment_id}/term/{term_id}/`

3) **Transcript**
- POST `/api/v1/assessment/transcripts/generate/`
- GET `/api/v1/assessment/transcripts/{id}/`

---

## ✅ Phase 5: Tests

- ReportCard generation uses VALIDATED grades only
- Absences excluded
- Rank calculation correct (ex-aequo)
- Transcript aggregates from ReportCards
- Permission checks on generation endpoints

---

## ✅ Success Criteria

- Reports are **persisted** and **frozen**
- Full generation per class uses fixed number of queries (no N+1)
- ReportCard accuracy matches grading rules
- Transcript matches aggregated ReportCards

---

## Dependencies
- Assessment domain (AssessmentSubject, StudentAssessment)
- Enrollment domain (StudentEnrollment)
- School Operations (SchoolYearCycleTerm)
