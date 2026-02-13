# Academic API Usage Guide (Frontend)

Base path: `/api/v1/academic/`

## Reference Endpoints (CRUD)
These endpoints manage academic reference data.

### Academic Years
- `GET /academic-years/`
- `POST /academic-years/`
- `GET /academic-years/{id}/`
- `PATCH /academic-years/{id}/`
- `DELETE /academic-years/{id}/`

### Cycles
- `GET /cycles/`
- `POST /cycles/`
- `GET /cycles/{id}/`
- `PATCH /cycles/{id}/`
- `DELETE /cycles/{id}/`

### Levels
- `GET /levels/`
- `POST /levels/`
- `GET /levels/{id}/`
- `PATCH /levels/{id}/`
- `DELETE /levels/{id}/`

### Tracks
- `GET /tracks/`
- `POST /tracks/`
- `GET /tracks/{id}/`
- `PATCH /tracks/{id}/`
- `DELETE /tracks/{id}/`

### Subjects
- `GET /subjects/`
- `POST /subjects/`
- `GET /subjects/{id}/`
- `PATCH /subjects/{id}/`
- `DELETE /subjects/{id}/`

### Assessment Types
- `GET /assessment-types/`
- `POST /assessment-types/`
- `GET /assessment-types/{id}/`
- `PATCH /assessment-types/{id}/`
- `DELETE /assessment-types/{id}/`

### Terms / Term Types
- `GET /term-types/`
- `POST /term-types/`
- `GET /term-types/{id}/`
- `PATCH /term-types/{id}/`
- `DELETE /term-types/{id}/`

- `GET /terms/`
- `POST /terms/`
- `GET /terms/{id}/`
- `PATCH /terms/{id}/`
- `DELETE /terms/{id}/`

---

Permissions follow the project’s default API policy (authenticated users with proper role).