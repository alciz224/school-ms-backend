# Assessment API Usage Guide (Frontend)

This document describes the **Assessment** API endpoints for frontend integration, with focus on bulk grading, reporting, and portal permissions.

> Base path: `/api/v1/assessment/`

---

## 1) Bulk Grading (Teacher)

### ✅ Preview (dry‑run)
**POST** `/assessment-subjects/{id}/grades/preview/`

**Payload:**
```json
{
  "grades": [
    {"enrollment_id": 101, "raw_score": 15.0},
    {"enrollment_id": 102, "raw_score": 18.0}
  ]
}
```

**Response (success):**
```json
{
  "assessment_subject_id": 55,
  "max_score": 20.0,
  "total": 2,
  "creates": 2,
  "updates": 0,
  "errors": []
}
```

**Response (preview errors):**
```json
{
  "errors": [
    {
      "index": 1,
      "enrollment_id": 102,
      "code": "score_exceeds_max",
      "detail": "Score cannot exceed maximum score (20)."
    }
  ],
  "creates": 1,
  "updates": 0,
  "total": 2,
  "max_score": 20.0,
  "assessment_subject_id": 55
}
```

**Error codes (preview):**
- `missing_enrollment_id`
- `not_in_classroom`
- `invalid_score`
- `negative_score`
- `score_exceeds_max`
- `absent_with_score`
- `score_required_when_present`
- `validation_error`

---

### ✅ Commit (atomic)
**POST** `/assessment-subjects/{id}/grades/commit/`

**Payload:** *(same as preview)*

**Response (success):**
```json
{
  "assessment_subject_id": 55,
  "created": 10,
  "updated": 5,
  "total": 15
}
```

**Response (error):**
```json
{
  "success": false,
  "error": {
    "code": "score_exceeds_max",
    "message": "Bulk commit validation failed.",
    "details": {
      "error": {
        "index": 1,
        "enrollment_id": 102,
        "code": "score_exceeds_max",
        "detail": "Score cannot exceed maximum score (20)."
      }
    }
  }
}
```

**Notes:**
- Commit is **all-or-nothing**. If any item fails, no grade is saved.
- Always call `preview` before `commit`.

---

## 2) Teacher Grading Sheet

**GET** `/assessment-subjects/{id}/grading-sheet/`

**Response:**
```json
{
  "assessment_subject_id": 55,
  "subject_name": "Math",
  "classroom_id": 12,
  "max_score": 20,
  "status": "PUBLISHED",
  "rows": [
    {
      "enrollment_id": 101,
      "display_name": "Mamadou 1 Diallo",
      "student_id": null,
      "existing_score": 15.0,
      "is_absent": false,
      "is_excused": false,
      "remark": ""
    }
  ]
}
```

---

## 3) Assessment Overview (Staff / Teacher)

**GET** `/assessments/{id}/overview/`

**Response:**
```json
{
  "assessment_id": 20,
  "name": "Trimester 1",
  "status": "ACTIVE",
  "start_date": "2025-09-01",
  "end_date": "2025-12-15",
  "subjects_total": 12,
  "subjects_by_status": {
    "PUBLISHED": 8,
    "DRAFT": 4
  }
}
```

---

## 4) Student Grades History (Student / Staff)

**GET** `/students/{enrollment_id}/grades/`

**Response:**
```json
[
  {
    "student_assessment_id": 1001,
    "assessment_name": "Trimester 1",
    "subject_name": "Math",
    "raw_score": 15.0,
    "max_score": 20,
    "is_absent": false,
    "is_excused": false,
    "status": "VALIDATED"
  }
]
```

---

## 5) Classroom Averages (Staff / Teacher)

**GET** `/classrooms/{id}/averages/`

**Response:**
```json
{
  "Math": {
    "average": 12.7,
    "max_score": 20,
    "count": 25
  }
}
```

---

## 6) Report Cards (Staff)

### Generate report cards
**POST** `/report-cards/generate/`
```json
{
  "classroom_id": 12,
  "term_id": 5,
  "force": true
}
```

**Response:**
```json
{
  "report_cards_created": 25,
  "report_cards_updated": 0,
  "subjects_created": 125
}
```

### Get student report card
**GET** `/report-cards/student/{enrollment_id}/term/{term_id}/`

### Get class report cards
**GET** `/report-cards/classroom/{classroom_id}/term/{term_id}/`

---

## 7) Transcripts (Staff)

### Generate transcript
**POST** `/transcripts/generate/`
```json
{
  "student_enrollment_id": 320,
  "school_year_id": 8
}
```

### Get transcript
**GET** `/transcripts/student/{enrollment_id}/year/{school_year_id}/`

---

## ✅ Permissions Summary

| Endpoint | Role Required |
|---------|---------------|
| Bulk preview/commit | TEACHER |
| Grading sheet | TEACHER |
| Assessment overview | STAFF / TEACHER |
| Student grades | STUDENT / STAFF |
| Classroom averages | STAFF / TEACHER |
| Report card generate | STAFF |
| Transcript generate | STAFF |

---

## ✅ Best Practices for Frontend

- Always call **preview** before commit (shows per-row validation errors).
- Use `errors[index]` to highlight invalid rows in Excel/CSV imports.
- Use structured error codes for UX mapping.
- Cache grading sheet data for teacher UI performance.

---

If you need a CSV upload flow or parsing guide, we can add it later.