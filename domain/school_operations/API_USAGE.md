# School Operations API Usage Guide (Frontend)

Base path: `/api/v1/school-operations/`

## Core Endpoints

### School Years
- `GET /school-years/`
- `POST /school-years/`
- `GET /school-years/{id}/`
- `PATCH /school-years/{id}/`
- `DELETE /school-years/{id}/`
- `POST /school-years/{id}/set_current/`

### School Year Cycles
- `GET /school-year-cycles/`
- `POST /school-year-cycles/`
- `GET /school-year-cycles/{id}/`
- `PATCH /school-year-cycles/{id}/`
- `DELETE /school-year-cycles/{id}/`

### School Year Cycle Terms
- `GET /school-year-cycle-terms/?school_year_cycle={id}`
- `POST /school-year-cycle-terms/`
- `GET /school-year-cycle-terms/{id}/`
- `PATCH /school-year-cycle-terms/{id}/`
- `DELETE /school-year-cycle-terms/{id}/`

### School Year Levels
- `GET /school-year-levels/?school_year_cycle={id}`
- `POST /school-year-levels/`
- `GET /school-year-levels/{id}/`
- `PATCH /school-year-levels/{id}/`
- `DELETE /school-year-levels/{id}/`

### School Year Level Subjects
- `GET /school-year-level-subjects/?school_year_level={id}`
- `POST /school-year-level-subjects/`
- `GET /school-year-level-subjects/{id}/`
- `PATCH /school-year-level-subjects/{id}/`
- `DELETE /school-year-level-subjects/{id}/`

---

Permissions follow the project’s default API policy (authenticated users with proper role).