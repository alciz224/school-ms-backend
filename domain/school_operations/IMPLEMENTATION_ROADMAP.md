# School Model - Implementation Roadmap

## Overview

This document provides a step-by-step implementation plan for the School model, following the established patterns in the codebase.

## Phase 1: Core Model Implementation

### Step 1.1: Create Constants
**File**: `domain/school_operations/constants.py`

**Tasks**:
- [ ] Define `SchoolType` enum (PUBLIC, PRIVATE, COMMUNITY, ISLAMIC, CONFESSIONAL)
- [ ] Define `SchoolLevel` enum (PRESCHOOL, PRIMARY, SECONDARY, PRIMARY_SECONDARY, COMPLETE)
- [ ] Define `SchoolStatus` enum (DRAFT, ACTIVE, SUSPENDED, CLOSED)

**Pattern Reference**: `domain/academic/constants.py`, `domain/geography/constants.py`

**Estimated Time**: 30 minutes

---

### Step 1.2: Create Validators
**File**: `domain/school_operations/validators.py`

**Tasks**:
- [ ] `validate_founded_year(value)`: Ensure not in future
- [ ] `validate_capacity(value)`: Ensure reasonable range (1-10000)
- [ ] `validate_school_phone(value)`: Validate international format (reuse or adapt from account)
- [ ] `validate_school_user(user)`: Ensure user is active

**Pattern Reference**: `domain/academic/validators.py`, `domain/account/validators.py`

**Estimated Time**: 45 minutes

---

### Step 1.3: Create School Model
**File**: `domain/school_operations/models/school.py`

**Tasks**:
- [ ] Define `SchoolManager` class (custom manager)
  - [ ] `by_locality(locality)` method
  - [ ] `by_administrative_unit(unit)` method
  - [ ] `by_region(region)` method
  - [ ] `by_type(school_type)` method
  - [ ] `active_operational()` method
  - [ ] `at_capacity()` method
  - [ ] `with_capacity()` method

- [ ] Define `School` model class (extends AuditModel)
  - [ ] Identity fields (code, name, short_name)
  - [ ] Classification fields (type, level, status)
  - [ ] Relationship fields (locality, director, registrar)
  - [ ] Contact fields (email, phone, phone_secondary, website, address_line1, address_line2, postal_code)
  - [ ] Operational fields (founded_year, capacity, current_enrollment)
  - [ ] Extensibility fields (settings, notes)
  - [ ] Meta class (db_table, verbose_name, ordering, indexes, constraints)
  - [ ] `__str__()` method
  - [ ] `clean()` method (validation)
  - [ ] `save()` method (call full_clean)
  - [ ] Instance methods:
    - [ ] `get_full_address()`
    - [ ] `get_geographic_path()`
    - [ ] `can_activate()`
    - [ ] `activate(user)`
    - [ ] `suspend(user, reason)`
    - [ ] `close(user, reason)`
    - [ ] `update_enrollment_count()`
    - [ ] `get_available_capacity()`
    - [ ] `is_at_capacity()`
    - [ ] `get_setting(key_path, default)`
    - [ ] `set_setting(key_path, value)`

**Pattern Reference**: `domain/academic/models/academic_year.py`, `domain/geography/models/locality.py`

**Estimated Time**: 3-4 hours

---

### Step 1.4: Update Models __init__
**File**: `domain/school_operations/models/__init__.py`

**Tasks**:
- [ ] Import and export `School` model
- [ ] Import and export `SchoolManager`

**Current Content**:
```python
# Empty or minimal
```

**New Content**:
```python
from .school import School, SchoolManager

__all__ = ['School', 'SchoolManager']
```

**Estimated Time**: 5 minutes

---

### Step 1.5: Create Migration
**Command**: `python manage.py makemigrations school_operations`

**Tasks**:
- [ ] Run makemigrations
- [ ] Review generated migration
- [ ] Test migration locally
- [ ] Create rollback plan

**Verification**:
```bash
python manage.py sqlmigrate school_operations 0001
python manage.py migrate school_operations --plan
```

**Estimated Time**: 30 minutes

---

## Phase 2: Admin Interface

### Step 2.1: Configure Admin
**File**: `domain/school_operations/admin.py`

**Tasks**:
- [ ] Create `SchoolAdmin` class
- [ ] Configure list_display: code, name, type, level, status, locality, is_active
- [ ] Configure list_filter: type, level, status, is_active, locality__administrative_unit__region
- [ ] Configure search_fields: code, name, short_name, email
- [ ] Configure readonly_fields: created_at, updated_at, created_by, current_enrollment
- [ ] Configure fieldsets (organized sections)
- [ ] Add custom actions: activate_schools, suspend_schools
- [ ] Configure inlines (if needed)

**Pattern Reference**: `domain/academic/admin.py`

**Estimated Time**: 1 hour

---

## Phase 3: Business Logic Layer

### Step 3.1: Create Selectors
**File**: `domain/school_operations/selectors/school.py`

**Tasks**:
- [ ] `get_school_by_id(school_id: int) -> School`
- [ ] `get_school_by_code(code: str) -> School`
- [ ] `list_schools(**filters) -> QuerySet[School]`
- [ ] `list_schools_by_locality(locality) -> QuerySet[School]`
- [ ] `list_schools_by_region(region) -> QuerySet[School]`
- [ ] `list_active_schools() -> QuerySet[School]`
- [ ] `list_schools_at_capacity() -> QuerySet[School]`
- [ ] `get_schools_statistics(filters) -> dict`

**Pattern**: Read-only query functions, no side effects

**Pattern Reference**: `domain/academic/selectors/academic_year.py`

**Estimated Time**: 1.5 hours

---

### Step 3.2: Create Services
**File**: `domain/school_operations/services/school.py`

**Tasks**:
- [ ] `create_school(user, **data) -> School`
- [ ] `update_school(school, user, **data) -> School`
- [ ] `delete_school(school, user) -> None`
- [ ] `restore_school(school, user) -> School`
- [ ] `activate_school(school, user) -> School`
- [ ] `suspend_school(school, user, reason: str) -> School`
- [ ] `close_school(school, user, reason: str) -> School`
- [ ] `assign_director(school, user, director_user) -> School`
- [ ] `assign_registrar(school, user, registrar_user) -> School`
- [ ] `update_enrollment_count(school) -> School`
- [ ] `update_school_settings(school, settings_dict) -> School`

**Pattern**: All write operations, returns modified objects, accepts user for audit

**Pattern Reference**: `domain/academic/services/academic_year.py`

**Estimated Time**: 2-3 hours

---

### Step 3.3: Update __init__ Files
**Files**: 
- `domain/school_operations/selectors/__init__.py`
- `domain/school_operations/services/__init__.py`

**Tasks**:
- [ ] Export selector functions
- [ ] Export service functions

**Estimated Time**: 10 minutes

---

## Phase 4: API Layer

### Step 4.1: Create Serializers
**File**: `domain/school_operations/api/serializers/school.py`

**Tasks**:
- [ ] `SchoolListSerializer` (lightweight for list views)
- [ ] `SchoolDetailSerializer` (complete details)
- [ ] `SchoolCreateSerializer` (input validation)
- [ ] `SchoolUpdateSerializer` (update validation)
- [ ] `SchoolSettingsSerializer` (settings CRUD)
- [ ] Add nested geography serializers (read-only)
- [ ] Add nested user serializers (read-only for director/registrar)

**Pattern Reference**: `domain/academic/api/serializers/academic_year.py`

**Estimated Time**: 2 hours

---

### Step 4.2: Create API Views
**File**: `domain/school_operations/api/views/school.py`

**Tasks**:
- [ ] `SchoolViewSet` (ModelViewSet)
  - [ ] list() - GET /schools/
  - [ ] retrieve() - GET /schools/{id}/
  - [ ] create() - POST /schools/
  - [ ] update() - PUT /schools/{id}/
  - [ ] partial_update() - PATCH /schools/{id}/
  - [ ] destroy() - DELETE /schools/{id}/
  - [ ] Custom actions:
    - [ ] @action activate - POST /schools/{id}/activate/
    - [ ] @action suspend - POST /schools/{id}/suspend/
    - [ ] @action close - POST /schools/{id}/close/
    - [ ] @action restore - POST /schools/{id}/restore/
    - [ ] @action statistics - GET /schools/statistics/
- [ ] Configure permissions
- [ ] Configure pagination
- [ ] Configure filtering (django-filter)
- [ ] Configure ordering

**Pattern Reference**: `domain/academic/api/views/academic_year.py`

**Estimated Time**: 2-3 hours

---

### Step 4.3: Create API Permissions
**File**: `domain/school_operations/api/permissions.py`

**Tasks**:
- [ ] `IsSchoolManager` permission
- [ ] `IsSchoolDirector` permission
- [ ] `CanManageSchool` permission (director or registrar)

**Pattern Reference**: `domain/academic/api/permissions.py`

**Estimated Time**: 1 hour

---

### Step 4.4: Configure URLs
**File**: `domain/school_operations/api/urls.py`

**Tasks**:
- [ ] Register SchoolViewSet with router
- [ ] Configure URL patterns
- [ ] Add to main API urls if needed

**Pattern Reference**: `domain/academic/api/urls.py`

**Estimated Time**: 30 minutes

---

### Step 4.5: Update __init__ Files
**Files**:
- `domain/school_operations/api/serializers/__init__.py`
- `domain/school_operations/api/views/__init__.py`

**Tasks**:
- [ ] Export serializers
- [ ] Export views

**Estimated Time**: 10 minutes

---

## Phase 5: Testing

### Step 5.1: Model Tests
**File**: `domain/school_operations/tests/test_models.py`

**Tasks**:
- [ ] Test school creation (valid data)
- [ ] Test school creation (invalid data)
- [ ] Test unique constraints (code, name per locality)
- [ ] Test check constraints (enrollment vs capacity)
- [ ] Test ForeignKey relationships (locality, users)
- [ ] Test soft delete
- [ ] Test restore
- [ ] Test status transitions
- [ ] Test manager methods
- [ ] Test model methods (get_full_address, can_activate, etc.)
- [ ] Test settings getter/setter
- [ ] Test validation (clean method)

**Pattern Reference**: `domain/academic/tests/test_models.py`

**Estimated Time**: 4-5 hours

---

### Step 5.2: Service Tests
**File**: `domain/school_operations/tests/test_services.py`

**Tasks**:
- [ ] Test create_school service
- [ ] Test update_school service
- [ ] Test delete_school service (soft delete)
- [ ] Test activate_school service
- [ ] Test suspend_school service
- [ ] Test close_school service
- [ ] Test assign_director service
- [ ] Test assign_registrar service
- [ ] Test update_enrollment_count service
- [ ] Test error cases (validation failures)
- [ ] Test audit trail (created_by, updated_by)

**Pattern Reference**: `domain/account/tests/test_services.py`

**Estimated Time**: 3-4 hours

---

### Step 5.3: API Tests
**File**: `domain/school_operations/tests/test_api.py`

**Tasks**:
- [ ] Test list schools endpoint
- [ ] Test retrieve school endpoint
- [ ] Test create school endpoint
- [ ] Test update school endpoint
- [ ] Test delete school endpoint
- [ ] Test activate action
- [ ] Test suspend action
- [ ] Test close action
- [ ] Test restore action
- [ ] Test filtering (by type, level, status, locality)
- [ ] Test ordering
- [ ] Test pagination
- [ ] Test permissions
- [ ] Test error responses

**Pattern Reference**: `domain/account/tests/test_api_user.py`

**Estimated Time**: 4-5 hours

---

### Step 5.4: Create Test Fixtures
**File**: `domain/school_operations/tests/conftest.py`

**Tasks**:
- [ ] Create pytest fixtures for:
  - [ ] `school_factory`
  - [ ] `sample_locality`
  - [ ] `sample_director`
  - [ ] `sample_registrar`
  - [ ] `sample_schools` (multiple)

**Pattern Reference**: `domain/account/tests/conftest.py`

**Estimated Time**: 1 hour

---

## Phase 6: Data Management

### Step 6.1: Create Seed Command
**File**: `domain/school_operations/management/commands/seed_schools.py`

**Tasks**:
- [ ] Create command class
- [ ] Generate sample schools (10-20)
- [ ] Various types (public, private, etc.)
- [ ] Various levels (preschool, primary, etc.)
- [ ] Various statuses (draft, active, etc.)
- [ ] Link to existing localities
- [ ] Generate realistic settings

**Pattern Reference**: `domain/academic/management/commands/seed_academic.py`

**Estimated Time**: 2 hours

---

## Phase 7: Documentation

### Step 7.1: API Documentation
**File**: `docs/api/school_operations.md` (create if needed)

**Tasks**:
- [ ] Document all endpoints
- [ ] Add request/response examples
- [ ] Document filters and ordering
- [ ] Document permissions
- [ ] Add error codes and messages

**Estimated Time**: 2 hours

---

### Step 7.2: Model Documentation
**File**: `docs/models/school.md` (create if needed)

**Tasks**:
- [ ] Document model fields
- [ ] Document relationships
- [ ] Document business rules
- [ ] Add usage examples
- [ ] Document settings structure

**Estimated Time**: 1.5 hours

---

### Step 7.3: Update Main Documentation
**Files**: 
- `README.md`
- `docs/architecture.md` (if exists)
- `CHANGELOG.md`

**Tasks**:
- [ ] Add school_operations to domain list
- [ ] Update architecture diagram
- [ ] Add changelog entry
- [ ] Update feature list

**Estimated Time**: 30 minutes

---

## Phase 8: Integration & Deployment

### Step 8.1: Integration Testing
**Tasks**:
- [ ] Test with real geography data
- [ ] Test with real user data
- [ ] Test cross-domain queries
- [ ] Test performance with large datasets
- [ ] Test migration on staging database

**Estimated Time**: 2-3 hours

---

### Step 8.2: Code Review
**Tasks**:
- [ ] Self-review all code
- [ ] Check code style (PEP 8, Black)
- [ ] Check docstrings
- [ ] Check type hints
- [ ] Run linters (flake8, pylint)
- [ ] Submit for team review

**Estimated Time**: 2 hours

---

### Step 8.3: Deployment
**Tasks**:
- [ ] Create deployment checklist
- [ ] Backup database
- [ ] Run migrations on production
- [ ] Verify migrations
- [ ] Run seed command (optional)
- [ ] Smoke tests
- [ ] Monitor for errors

**Estimated Time**: 1-2 hours

---

## Summary

### Total Estimated Time
- **Phase 1**: Core Model - 5-6 hours
- **Phase 2**: Admin - 1 hour
- **Phase 3**: Business Logic - 4-5 hours
- **Phase 4**: API - 6-7 hours
- **Phase 5**: Testing - 12-15 hours
- **Phase 6**: Data Management - 2 hours
- **Phase 7**: Documentation - 4 hours
- **Phase 8**: Integration & Deployment - 5-7 hours

**Total**: 39-51 hours (approximately 5-7 working days)

### Priority Order

**High Priority** (Must have for MVP):
1. Phase 1: Core Model Implementation
2. Phase 5.1: Model Tests
3. Phase 3: Business Logic Layer
4. Phase 4: API Layer
5. Phase 5.2-5.3: Service & API Tests

**Medium Priority** (Important but can follow):
6. Phase 2: Admin Interface
7. Phase 6: Data Management (Seed Command)

**Low Priority** (Can be done later):
8. Phase 7: Documentation
9. Advanced features (Phase 8)

### Dependencies

```
Phase 1 (Core Model)
    ↓
Phase 5.1 (Model Tests)
    ↓
Phase 3 (Business Logic) + Phase 2 (Admin)
    ↓
Phase 4 (API Layer)
    ↓
Phase 5.2-5.3 (Service & API Tests)
    ↓
Phase 6 (Seed Command)
    ↓
Phase 7 (Documentation)
    ↓
Phase 8 (Integration & Deployment)
```

### Success Criteria

**Phase Completion Checklist**:
- [ ] All tests passing (100% pass rate)
- [ ] Test coverage > 90% for school module
- [ ] No linting errors
- [ ] All docstrings complete
- [ ] API endpoints functional
- [ ] Admin interface working
- [ ] Migrations successful
- [ ] Seed command working
- [ ] Documentation complete
- [ ] Code reviewed and approved

### Risk Mitigation

**Potential Risks**:
1. **Performance**: School queries with deep geography joins
   - **Mitigation**: Use select_related, proper indexing
   
2. **Data Integrity**: Soft delete complexity
   - **Mitigation**: Comprehensive constraint tests
   
3. **Status Transitions**: Complex state machine
   - **Mitigation**: Explicit validation in clean() method
   
4. **Settings JSONField**: Unstructured data
   - **Mitigation**: Default structure, validation, helper methods

### Next Steps After School Model

**Future Models to Implement**:
1. **SchoolYear** (bridge between School + AcademicYear)
2. **Enrollment** (student enrollments)
3. **ClassSection** (classes/sections)
4. **Staff** (teacher/staff assignments)

**Order of Implementation**:
```
School (foundational)
    ↓
SchoolYear (operational period)
    ↓
ClassSection (organizational unit)
    ↓
Enrollment (student assignment)
    ↓
Staff (teacher assignment)
```

## Quick Start Guide

### For Developers Starting Implementation

**Day 1**: Core Model
```bash
# 1. Create constants
# Edit: domain/school_operations/constants.py

# 2. Create validators
# Edit: domain/school_operations/validators.py

# 3. Create model
# Edit: domain/school_operations/models/school.py

# 4. Update __init__
# Edit: domain/school_operations/models/__init__.py

# 5. Create migration
python manage.py makemigrations school_operations
python manage.py migrate school_operations

# 6. Write model tests
# Edit: domain/school_operations/tests/test_models.py
pytest domain/school_operations/tests/test_models.py
```

**Day 2**: Business Logic
```bash
# 1. Create selectors
# Edit: domain/school_operations/selectors/school.py

# 2. Create services
# Edit: domain/school_operations/services/school.py

# 3. Write service tests
# Edit: domain/school_operations/tests/test_services.py
pytest domain/school_operations/tests/test_services.py
```

**Day 3**: API Layer
```bash
# 1. Create serializers
# Edit: domain/school_operations/api/serializers/school.py

# 2. Create views
# Edit: domain/school_operations/api/views/school.py

# 3. Configure URLs
# Edit: domain/school_operations/api/urls.py

# 4. Write API tests
# Edit: domain/school_operations/tests/test_api.py
pytest domain/school_operations/tests/test_api.py
```

**Day 4**: Admin & Data
```bash
# 1. Configure admin
# Edit: domain/school_operations/admin.py

# 2. Create seed command
# Edit: domain/school_operations/management/commands/seed_schools.py
python manage.py seed_schools

# 3. Test in admin
python manage.py runserver
# Visit http://localhost:8000/admin/
```

**Day 5**: Documentation & Polish
```bash
# 1. Write documentation
# 2. Code review
# 3. Final testing
# 4. Deployment preparation
```
