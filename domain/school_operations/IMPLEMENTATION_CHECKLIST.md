# School Model - Implementation Checklist

## Pre-Implementation Review

### Design Review
- [ ] Read [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)
- [ ] Read [SCHOOL_MODEL_OVERVIEW.md](./SCHOOL_MODEL_OVERVIEW.md)
- [ ] Read [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md)
- [ ] Read [KEY_DECISIONS.md](./KEY_DECISIONS.md)
- [ ] Review [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
- [ ] Team design review completed
- [ ] Design approved by tech lead

### Environment Setup
- [ ] Development environment ready
- [ ] Database backup created
- [ ] Git branch created (`feature/school-model` or similar)
- [ ] Virtual environment activated
- [ ] Dependencies up to date (`pip install -r requirements.txt`)

---

## Phase 1: Core Model Implementation

### 1.1 Constants (domain/school_operations/constants.py)
- [ ] File created
- [ ] Import statements added (django.db.models, gettext_lazy)
- [ ] SchoolType enum defined
  - [ ] PUBLIC
  - [ ] PRIVATE
  - [ ] COMMUNITY
  - [ ] ISLAMIC
  - [ ] CONFESSIONAL
- [ ] SchoolLevel enum defined
  - [ ] PRESCHOOL
  - [ ] PRIMARY
  - [ ] SECONDARY
  - [ ] PRIMARY_SECONDARY
  - [ ] COMPLETE
- [ ] SchoolStatus enum defined
  - [ ] DRAFT
  - [ ] ACTIVE
  - [ ] SUSPENDED
  - [ ] CLOSED
- [ ] All enums use TextChoices pattern
- [ ] All enums have translations (_())
- [ ] File tested (import successfully)

### 1.2 Validators (domain/school_operations/validators.py)
- [ ] File created
- [ ] Import statements added
- [ ] validate_founded_year(value) implemented
  - [ ] Check not in future
  - [ ] Raise ValidationError if invalid
- [ ] validate_capacity(value) implemented
  - [ ] Check range (1-10000)
  - [ ] Raise ValidationError if invalid
- [ ] validate_school_phone(value) implemented
  - [ ] Reuse/adapt from account validators
  - [ ] International format check
- [ ] validate_school_user(user) implemented
  - [ ] Check user.is_active
  - [ ] Check not user.is_deleted (if applicable)
- [ ] All validators have docstrings
- [ ] Unit tests written (test_validators.py)

### 1.3 School Model (domain/school_operations/models/school.py)

#### Manager Implementation
- [ ] SchoolManager class created
- [ ] Extends BaseManager
- [ ] by_locality(locality) method implemented
- [ ] by_administrative_unit(unit) method implemented
- [ ] by_region(region) method implemented
- [ ] by_type(school_type) method implemented
- [ ] active_operational() method implemented
- [ ] at_capacity() method implemented
- [ ] with_capacity() method implemented
- [ ] All methods have docstrings

#### School Model - Imports
- [ ] Import AuditModel
- [ ] Import models from django.db
- [ ] Import gettext_lazy
- [ ] Import settings (AUTH_USER_MODEL)
- [ ] Import constants (SchoolType, SchoolLevel, SchoolStatus)
- [ ] Import validators

#### School Model - Fields (Identity)
- [ ] code field (CharField, max_length=20)
  - [ ] unique=True
  - [ ] blank=True (auto-generated)
  - [ ] db_index=True
  - [ ] help_text added
- [ ] name field (CharField, max_length=200)
  - [ ] db_index=True
  - [ ] help_text added
- [ ] short_name field (CharField, max_length=100)
  - [ ] blank=True, null=True
  - [ ] help_text added

#### School Model - Fields (Classification)
- [ ] type field (CharField, choices)
  - [ ] choices=SchoolType.choices
  - [ ] db_index=True
  - [ ] help_text added
- [ ] level field (CharField, choices)
  - [ ] choices=SchoolLevel.choices
  - [ ] db_index=True
  - [ ] help_text added
- [ ] status field (CharField, choices)
  - [ ] choices=SchoolStatus.choices
  - [ ] default=SchoolStatus.DRAFT
  - [ ] db_index=True
  - [ ] help_text added

#### School Model - Fields (Relationships)
- [ ] locality field (ForeignKey)
  - [ ] to='geography.Locality'
  - [ ] on_delete=models.PROTECT
  - [ ] related_name='schools'
  - [ ] verbose_name with translation
- [ ] director field (ForeignKey)
  - [ ] to=settings.AUTH_USER_MODEL
  - [ ] on_delete=models.SET_NULL
  - [ ] null=True, blank=True
  - [ ] related_name='schools_as_director'
  - [ ] verbose_name with translation
- [ ] registrar field (ForeignKey)
  - [ ] to=settings.AUTH_USER_MODEL
  - [ ] on_delete=models.SET_NULL
  - [ ] null=True, blank=True
  - [ ] related_name='schools_as_registrar'
  - [ ] verbose_name with translation

#### School Model - Fields (Contact)
- [ ] email field (EmailField)
  - [ ] blank=True, null=True
  - [ ] help_text added
- [ ] phone field (CharField, max_length=20)
  - [ ] blank=True, null=True
  - [ ] validators=[validate_school_phone]
  - [ ] help_text added
- [ ] phone_secondary field (CharField, max_length=20)
  - [ ] blank=True, null=True
  - [ ] help_text added
- [ ] website field (URLField)
  - [ ] blank=True, null=True
  - [ ] help_text added
- [ ] address_line1 field (CharField, max_length=255)
  - [ ] blank=True, null=True
- [ ] address_line2 field (CharField, max_length=255)
  - [ ] blank=True, null=True
- [ ] postal_code field (CharField, max_length=20)
  - [ ] blank=True, null=True

#### School Model - Fields (Operations)
- [ ] founded_year field (PositiveIntegerField)
  - [ ] blank=True, null=True
  - [ ] validators=[validate_founded_year]
  - [ ] help_text added
- [ ] capacity field (PositiveIntegerField)
  - [ ] blank=True, null=True
  - [ ] validators=[validate_capacity]
  - [ ] help_text added
- [ ] current_enrollment field (PositiveIntegerField)
  - [ ] default=0
  - [ ] db_index=True
  - [ ] help_text added

#### School Model - Fields (Extensibility)
- [ ] settings field (JSONField)
  - [ ] default=dict
  - [ ] blank=True
  - [ ] help_text added
- [ ] notes field (TextField)
  - [ ] blank=True
  - [ ] help_text added

#### School Model - Manager Assignment
- [ ] objects = SchoolManager()

#### School Model - Meta Class
- [ ] db_table = "school"
- [ ] verbose_name = "School"
- [ ] verbose_name_plural = "Schools"
- [ ] ordering = ["locality__administrative_unit__region", "name"]
- [ ] indexes list created (6 indexes)
  - [ ] school_code_idx
  - [ ] school_type_status_idx
  - [ ] school_level_idx
  - [ ] school_locality_name_idx
  - [ ] school_status_active_idx
  - [ ] school_enrollment_idx
- [ ] constraints list created (3 constraints)
  - [ ] unique_school_code (with is_deleted condition)
  - [ ] unique_school_name_per_locality (with is_deleted condition)
  - [ ] school_enrollment_within_capacity (CheckConstraint)

#### School Model - Methods (Basic)
- [ ] __str__() method implemented
  - [ ] Returns: f"{self.name} ({self.code})"
- [ ] clean() method implemented
  - [ ] Calls super().clean()
  - [ ] Validates capacity vs enrollment
  - [ ] Validates founded_year not future
  - [ ] Validates locality not deleted
  - [ ] Validates director is active (if set)
  - [ ] Validates registrar is active (if set)
- [ ] save() method implemented
  - [ ] Calls self.full_clean()
  - [ ] Calls super().save()

#### School Model - Methods (Business)
- [ ] get_full_address() implemented
  - [ ] Returns formatted address string
  - [ ] Includes locality information
- [ ] get_geographic_path() implemented
  - [ ] Returns full hierarchy string
  - [ ] Uses locality.full_path
- [ ] can_activate() implemented
  - [ ] Returns (bool, [errors])
  - [ ] Checks required fields
  - [ ] Checks status is DRAFT
- [ ] activate(user) implemented
  - [ ] Validates can_activate
  - [ ] Sets status=ACTIVE, is_active=True
  - [ ] Calls save_by(user)
- [ ] suspend(user, reason) implemented
  - [ ] Sets status=SUSPENDED
  - [ ] Logs reason (in notes or separate log)
  - [ ] Calls save_by(user)
- [ ] close(user, reason) implemented
  - [ ] Sets status=CLOSED, is_active=False
  - [ ] Logs reason
  - [ ] Calls save_by(user)
- [ ] update_enrollment_count() implemented
  - [ ] Calculates from enrollments (or placeholder)
  - [ ] Updates current_enrollment
  - [ ] Returns new count
- [ ] get_available_capacity() implemented
  - [ ] Returns capacity - current_enrollment
  - [ ] Returns None if capacity not set
- [ ] is_at_capacity() implemented
  - [ ] Returns bool
  - [ ] Handles capacity=None case

#### School Model - Methods (Settings)
- [ ] get_setting(key_path, default) implemented
  - [ ] Splits key_path by '.'
  - [ ] Traverses settings dict
  - [ ] Returns value or default
- [ ] set_setting(key_path, value) implemented
  - [ ] Splits key_path by '.'
  - [ ] Creates nested dicts as needed
  - [ ] Sets value

#### Documentation
- [ ] Model class docstring complete
- [ ] All methods have docstrings
- [ ] Field help_text all filled
- [ ] Business rules documented in docstring

### 1.4 Update models/__init__.py
- [ ] Import School
- [ ] Import SchoolManager
- [ ] Add to __all__
- [ ] File can be imported successfully

### 1.5 Create Migration
- [ ] Run `python manage.py makemigrations school_operations`
- [ ] Migration file created (0001_initial.py)
- [ ] Review migration SQL: `python manage.py sqlmigrate school_operations 0001`
- [ ] Verify all fields present
- [ ] Verify all indexes present
- [ ] Verify all constraints present
- [ ] Test migration: `python manage.py migrate school_operations`
- [ ] Migration successful
- [ ] Verify schema in database
- [ ] Test rollback: `python manage.py migrate school_operations zero`
- [ ] Test re-apply: `python manage.py migrate school_operations`

---

## Phase 2: Admin Interface

### 2.1 Admin Configuration (domain/school_operations/admin.py)
- [ ] Import School model
- [ ] Import admin from django.contrib
- [ ] Create SchoolAdmin class
- [ ] Configure list_display
  - [ ] code, name, type, level, status, locality, is_active
- [ ] Configure list_filter
  - [ ] type, level, status, is_active
  - [ ] locality__administrative_unit__region
- [ ] Configure search_fields
  - [ ] code, name, short_name, email
- [ ] Configure readonly_fields
  - [ ] created_at, updated_at, created_by, updated_by
  - [ ] deleted_at, deleted_by (if exposed)
  - [ ] current_enrollment
- [ ] Configure fieldsets (organized groups)
  - [ ] Identity section
  - [ ] Classification section
  - [ ] Location section
  - [ ] Contact section
  - [ ] Operations section
  - [ ] Settings section
  - [ ] Audit section
- [ ] Add custom actions
  - [ ] activate_schools
  - [ ] suspend_schools
- [ ] Register with admin.site.register()
- [ ] Test admin interface loads
- [ ] Test creating school via admin
- [ ] Test editing school via admin
- [ ] Test custom actions work

---

## Phase 3: Business Logic Layer

### 3.1 Selectors (domain/school_operations/selectors/school.py)
- [ ] File created
- [ ] Import statements added
- [ ] get_school_by_id(school_id) implemented
  - [ ] Returns School or raises DoesNotExist
  - [ ] Includes select_related for efficiency
- [ ] get_school_by_code(code) implemented
  - [ ] Returns School or raises DoesNotExist
- [ ] list_schools(**filters) implemented
  - [ ] Returns QuerySet
  - [ ] Supports filtering
  - [ ] Uses select_related for locality
- [ ] list_schools_by_locality(locality) implemented
- [ ] list_schools_by_region(region) implemented
- [ ] list_active_schools() implemented
- [ ] list_schools_at_capacity() implemented
- [ ] get_schools_statistics(filters) implemented
  - [ ] Returns dict with counts, aggregations
- [ ] All functions have docstrings
- [ ] All functions have type hints

### 3.2 Services (domain/school_operations/services/school.py)
- [ ] File created
- [ ] Import statements added
- [ ] create_school(user, **data) implemented
  - [ ] Validates data
  - [ ] Creates School instance
  - [ ] Uses save_by(user)
  - [ ] Returns School
- [ ] update_school(school, user, **data) implemented
  - [ ] Updates fields
  - [ ] Uses save_by(user)
  - [ ] Returns School
- [ ] delete_school(school, user) implemented
  - [ ] Soft deletes
  - [ ] Uses soft_delete(user)
- [ ] restore_school(school, user) implemented
  - [ ] Restores deleted school
  - [ ] Uses restore()
- [ ] activate_school(school, user) implemented
  - [ ] Calls school.activate(user)
  - [ ] Returns School
- [ ] suspend_school(school, user, reason) implemented
  - [ ] Calls school.suspend(user, reason)
  - [ ] Returns School
- [ ] close_school(school, user, reason) implemented
  - [ ] Calls school.close(user, reason)
  - [ ] Returns School
- [ ] assign_director(school, user, director_user) implemented
- [ ] assign_registrar(school, user, registrar_user) implemented
- [ ] update_enrollment_count(school) implemented
  - [ ] Calls school.update_enrollment_count()
  - [ ] Returns School
- [ ] update_school_settings(school, settings_dict) implemented
  - [ ] Validates settings structure
  - [ ] Updates settings
  - [ ] Saves
- [ ] All functions have docstrings
- [ ] All functions have type hints
- [ ] All functions handle errors appropriately

### 3.3 Update __init__ Files
- [ ] selectors/__init__.py exports all selectors
- [ ] services/__init__.py exports all services
- [ ] Can import from package level

---

## Phase 4: API Layer

### 4.1 Serializers (domain/school_operations/api/serializers/school.py)
- [ ] File created
- [ ] Import statements added
- [ ] LocalityNestedSerializer created (read-only)
- [ ] UserNestedSerializer created (read-only)
- [ ] SchoolListSerializer created
  - [ ] Lightweight fields
  - [ ] Nested locality (read-only)
  - [ ] Meta class configured
- [ ] SchoolDetailSerializer created
  - [ ] All fields
  - [ ] Nested locality, director, registrar (read-only)
  - [ ] Meta class configured
- [ ] SchoolCreateSerializer created
  - [ ] Input validation
  - [ ] Required fields only
  - [ ] Meta class configured
- [ ] SchoolUpdateSerializer created
  - [ ] Partial update support
  - [ ] Meta class configured
- [ ] SchoolSettingsSerializer created
  - [ ] For settings CRUD
  - [ ] Validation of structure
- [ ] All serializers have docstrings
- [ ] Test serialization works
- [ ] Test deserialization works

### 4.2 Views (domain/school_operations/api/views/school.py)
- [ ] File created
- [ ] Import statements added
- [ ] SchoolViewSet created (ModelViewSet)
- [ ] queryset configured
- [ ] get_serializer_class() implemented
  - [ ] Different serializers for different actions
- [ ] get_queryset() implemented
  - [ ] Optimized with select_related
  - [ ] Filtered appropriately
- [ ] list() action (default)
- [ ] retrieve() action (default)
- [ ] create() action customized
  - [ ] Calls create_school service
  - [ ] Uses request.user
- [ ] update() action customized
  - [ ] Calls update_school service
- [ ] partial_update() action customized
- [ ] destroy() action customized
  - [ ] Calls delete_school service (soft delete)
- [ ] @action activate implemented
  - [ ] POST /schools/{id}/activate/
  - [ ] Calls activate_school service
- [ ] @action suspend implemented
  - [ ] POST /schools/{id}/suspend/
  - [ ] Accepts reason in body
- [ ] @action close implemented
  - [ ] POST /schools/{id}/close/
  - [ ] Accepts reason in body
- [ ] @action restore implemented
  - [ ] POST /schools/{id}/restore/
- [ ] @action statistics implemented (list route)
  - [ ] GET /schools/statistics/
  - [ ] Returns aggregated data
- [ ] Permissions configured
- [ ] Pagination configured
- [ ] Filtering configured (django-filter)
  - [ ] type, level, status, locality
- [ ] Ordering configured
  - [ ] name, created_at, etc.
- [ ] All actions have docstrings
- [ ] Error handling implemented

### 4.3 Permissions (domain/school_operations/api/permissions.py)
- [ ] File created
- [ ] IsSchoolManager permission created
- [ ] IsSchoolDirector permission created
- [ ] CanManageSchool permission created
- [ ] All permissions have docstrings
- [ ] Test permissions work correctly

### 4.4 URLs (domain/school_operations/api/urls.py)
- [ ] File created
- [ ] Router imported and created
- [ ] SchoolViewSet registered
- [ ] urlpatterns defined
- [ ] Test URLs resolve correctly
- [ ] Integrate into main API urls (if needed)

### 4.5 Update __init__ Files
- [ ] api/serializers/__init__.py exports serializers
- [ ] api/views/__init__.py exports views
- [ ] Can import from package level

---

## Phase 5: Testing

### 5.1 Test Configuration (domain/school_operations/tests/conftest.py)
- [ ] File created
- [ ] Import pytest
- [ ] Import factories (if using factory_boy)
- [ ] school_factory fixture created
- [ ] sample_locality fixture created
- [ ] sample_director fixture created
- [ ] sample_registrar fixture created
- [ ] sample_schools fixture created (multiple)
- [ ] All fixtures working

### 5.2 Model Tests (domain/school_operations/tests/test_models.py)
- [ ] File created
- [ ] test_create_school_valid_data
- [ ] test_create_school_invalid_data
- [ ] test_unique_code_constraint
- [ ] test_unique_name_per_locality_constraint
- [ ] test_enrollment_capacity_constraint
- [ ] test_locality_relationship
- [ ] test_director_relationship
- [ ] test_registrar_relationship
- [ ] test_soft_delete
- [ ] test_restore
- [ ] test_status_draft_to_active
- [ ] test_status_active_to_suspended
- [ ] test_status_suspended_to_active
- [ ] test_status_to_closed
- [ ] test_manager_by_locality
- [ ] test_manager_by_region
- [ ] test_manager_active_operational
- [ ] test_manager_at_capacity
- [ ] test_get_full_address
- [ ] test_get_geographic_path
- [ ] test_can_activate
- [ ] test_activate
- [ ] test_suspend
- [ ] test_close
- [ ] test_update_enrollment_count
- [ ] test_get_available_capacity
- [ ] test_is_at_capacity
- [ ] test_get_setting
- [ ] test_set_setting
- [ ] test_clean_validation
- [ ] All tests passing
- [ ] Coverage > 95%

### 5.3 Service Tests (domain/school_operations/tests/test_services.py)
- [ ] File created
- [ ] test_create_school_success
- [ ] test_create_school_validation_error
- [ ] test_update_school_success
- [ ] test_update_school_validation_error
- [ ] test_delete_school
- [ ] test_restore_school
- [ ] test_activate_school_success
- [ ] test_activate_school_not_ready
- [ ] test_suspend_school
- [ ] test_close_school
- [ ] test_assign_director
- [ ] test_assign_registrar
- [ ] test_update_enrollment_count
- [ ] test_update_school_settings
- [ ] test_audit_trail_created_by
- [ ] test_audit_trail_updated_by
- [ ] All tests passing
- [ ] Coverage > 90%

### 5.4 API Tests (domain/school_operations/tests/test_api.py)
- [ ] File created
- [ ] test_list_schools
- [ ] test_list_schools_filtering
- [ ] test_list_schools_ordering
- [ ] test_list_schools_pagination
- [ ] test_retrieve_school
- [ ] test_create_school_valid
- [ ] test_create_school_invalid
- [ ] test_update_school
- [ ] test_partial_update_school
- [ ] test_delete_school
- [ ] test_activate_action
- [ ] test_suspend_action
- [ ] test_close_action
- [ ] test_restore_action
- [ ] test_statistics_action
- [ ] test_permissions_anonymous
- [ ] test_permissions_authenticated
- [ ] test_permissions_director
- [ ] test_error_responses_404
- [ ] test_error_responses_400
- [ ] All tests passing
- [ ] Coverage > 90%

### 5.5 Run All Tests
- [ ] Run: `pytest domain/school_operations/tests/`
- [ ] All tests passing
- [ ] No warnings
- [ ] Coverage report generated
- [ ] Coverage > 90% overall

---

## Phase 6: Data Management

### 6.1 Seed Command (domain/school_operations/management/commands/seed_schools.py)
- [ ] File created
- [ ] Import BaseCommand
- [ ] Import models
- [ ] Command class created
- [ ] handle() method implemented
- [ ] Generates 10-20 sample schools
- [ ] Various types (public, private, etc.)
- [ ] Various levels (preschool, primary, etc.)
- [ ] Various statuses (draft, active, etc.)
- [ ] Links to existing localities
- [ ] Generates realistic settings
- [ ] Idempotent (can run multiple times)
- [ ] Add --clear option to clear existing
- [ ] Test: `python manage.py seed_schools`
- [ ] Verify data in database
- [ ] Verify data in admin interface

---

## Phase 7: Documentation

### 7.1 API Documentation
- [ ] Document all endpoints
- [ ] Add request examples
- [ ] Add response examples
- [ ] Document query parameters
- [ ] Document filters
- [ ] Document ordering options
- [ ] Document pagination
- [ ] Document permissions
- [ ] Document error codes
- [ ] Add Postman collection (optional)

### 7.2 Update Main Documentation
- [ ] Update README.md
  - [ ] Add school_operations to features
  - [ ] Add usage examples
- [ ] Update CHANGELOG.md
  - [ ] Add entry for School model
- [ ] Update architecture docs (if exists)
  - [ ] Add School to domain diagram

---

## Phase 8: Integration & Deployment

### 8.1 Integration Testing
- [ ] Test with real geography data
- [ ] Test with real user accounts
- [ ] Test cross-domain queries
- [ ] Performance test with 1000+ schools
- [ ] Test on staging environment
- [ ] Test migrations on staging database

### 8.2 Code Quality
- [ ] Run Black: `black domain/school_operations/`
- [ ] Run flake8: `flake8 domain/school_operations/`
- [ ] Run pylint: `pylint domain/school_operations/`
- [ ] Run mypy: `mypy domain/school_operations/` (if using type checking)
- [ ] Fix all linting errors
- [ ] Fix all type errors

### 8.3 Code Review
- [ ] Self-review all code
- [ ] Check all docstrings
- [ ] Check all type hints
- [ ] Check all tests
- [ ] Create pull request
- [ ] Address review comments
- [ ] Get approval

### 8.4 Pre-Deployment
- [ ] Create deployment checklist
- [ ] Backup production database
- [ ] Test migration on copy of production data
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window (if needed)

### 8.5 Deployment
- [ ] Deploy to staging
- [ ] Run migrations on staging
- [ ] Smoke test on staging
- [ ] Deploy to production
- [ ] Run migrations on production
- [ ] Verify migrations successful
- [ ] Run seed command (optional)
- [ ] Smoke test on production
- [ ] Monitor for errors
- [ ] Monitor performance

### 8.6 Post-Deployment
- [ ] Verify all endpoints working
- [ ] Verify admin interface working
- [ ] Check error logs
- [ ] Check performance metrics
- [ ] Update team on completion
- [ ] Close related tickets

---

## Final Verification

### Code Complete
- [ ] All files created
- [ ] All functions implemented
- [ ] All tests written and passing
- [ ] All documentation complete
- [ ] Code reviewed and approved
- [ ] No TODO comments remaining
- [ ] No placeholder code remaining

### Quality Gates
- [ ] Test coverage > 90%
- [ ] No linting errors
- [ ] No type errors (if using mypy)
- [ ] All docstrings present
- [ ] Performance acceptable (< 100ms queries)

### Documentation Complete
- [ ] All design docs reviewed
- [ ] API documentation complete
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] Team trained (if needed)

### Deployment Complete
- [ ] Migrations successful
- [ ] Application running
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Monitoring configured

---

## Sign-Off

**Implementation Completed By**: ___________________

**Date**: ___________________

**Code Reviewed By**: ___________________

**Date**: ___________________

**Deployed By**: ___________________

**Date**: ___________________

**Sign-Off By Tech Lead**: ___________________

**Date**: ___________________

---

## Notes

Use this section for implementation notes, issues encountered, or deviations from the plan:

```
[Add notes here during implementation]
```
