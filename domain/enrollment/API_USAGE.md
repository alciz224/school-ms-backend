# Enrollment API Usage Guide (Frontend)

Base path: `/api/v1/enrollment/`

## Admin/Staff CRUD

### Classrooms
- `GET /classrooms/`
- `POST /classrooms/`
- `GET /classrooms/{id}/`
- `PATCH /classrooms/{id}/`
- `DELETE /classrooms/{id}/`

### Student Enrollments
- `GET /student-enrollments/`
- `POST /student-enrollments/`
- `GET /student-enrollments/{id}/`
- `PATCH /student-enrollments/{id}/`
- `DELETE /student-enrollments/{id}/`
- `POST /student-enrollments/{id}/transfer/`

### Teacher Assignments
- `GET /teacher-assignments/`
- `POST /teacher-assignments/`
- `PATCH /teacher-assignments/{id}/`
- `DELETE /teacher-assignments/{id}/`
- `POST /teacher-assignments/{id}/end/`
- `POST /teacher-assignments/{id}/replace/`

## Portal Roster Endpoints

### Staff / Admin
- `GET /roster/classrooms/`
- `GET /roster/classrooms/{id}/students/`
- `GET /roster/classrooms/{id}/stats/`
- `GET /roster/school-year-levels/{id}/enrollments/`

### Teacher
- `GET /roster/my-classes/`

### Student
- `GET /roster/me/`

### Parent
- `GET /roster/my-children/`

---

Permissions are based on session `current_role` (SCHOOL_ADMIN / STAFF / TEACHER / STUDENT / PARENT).