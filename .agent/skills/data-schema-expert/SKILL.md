---
name: Data Schema & Integrity Expert
description: Expert knowledge of the project's data schema, business logic constraints, and testing caveats. Read this skill before writing tests, factory fixtures, or performing database operations.
---

# Data Schema & Integrity Guide

This skill provides critical context about how the database, models, and business logic are structured in this project, particularly to help avoid common testing and data integrity pitfalls.

## 1. Soft Deletion & AuditModel constraints
All core business models inherit from `AuditModel`.
- **Soft Delete Rule:** To soft delete an item, you must use the `soft_delete()` method or ensure `is_active = False` is set when `is_deleted = True`. 
- **Validation Trap:** `AuditModel.clean()` explicitly enforces that `is_deleted` and `is_active` cannot both be true.
  ```python
  # DO NOT DO THIS (Raises ValidationError):
  obj.is_deleted = True
  obj.save() # Fails in full_clean()

  # DO THIS INSTEAD:
  obj.is_deleted = True
  obj.is_active = False
  obj.save()
  # Or better:
  obj.soft_delete(user=request.user)
  ```

## 2. Model Creation and Required Fields
When creating test fixtures or mocking data, respect the relationships and `NOT NULL` constraints across domains:

- **School (`domain/school_operations`)**: Strictly requires a valid `locality` (which cascades up to `AdministrativeUnit`, `RegionAdministrative`, and `Country`). It cannot be instantiated without one.
- **AcademicYear (`domain/academic`)**: Uses integer fields (`start_year` and `end_year`), NOT dates (`start_date`/`end_date`).
- **SchoolYear (`domain/school_operations`)**: Requires `academic_year`, `start_date`, `end_date`, AND a string `name` field.
- **SchoolYearCycle (`domain/school_operations`)**: Requires a `term_type` (e.g. Trimester, Semester) mapped to a valid `TermType` record.
- **Level (`domain/academic`)**: Has an `order` integer field, but **`Cycle`** does not.

## 3. Exception Handling Conventions
Domain-specific exceptions like `ValidationException`, `NotFoundException`, `ConflictException`, and `BusinessRuleException` are defined in `domain/shared/exceptions.py`.

- **BusinessRuleException Trap:** The string `rule` argument is stored within the `details` dictionary property, not directly on the exception object.
  ```python
  # IN TESTS:
  # Do not assert exc_info.value.rule == "my_rule"
  # Instead assert:
  assert exc_info.value.rule == "my_rule" # (If the property is exposed on the class)
  # Or:
  assert exc_info.value.details.get("rule") == "my_rule"
  ```

## 4. Choice Fields and Enums
Always use the exact uppercase variants provided by the constants when testing choice fields to avoid validation errors:
- `relationship_type` on `ParentChild` expects uppercase constants (e.g. `"FATHER"`, not `"father"`).
- `status` fields often use uppercase enum properties (e.g. `"ACTIVE"`, not `"active"`).

## 5. Frontend as Source of Truth
Never guess the schema for the API. The TypeScript types in the frontend (`src/server/data/{domain}/types.ts`) are the strict source of truth for all backend JSON inputs/outputs. (See the `frontend-contract-sync` skill for more details).

## 6. Business Logic Separation
- **Writes / Validations:** Belong in `domain/{domain}/services/{model}.py`. Use keyword-only arguments and `@staticmethod`.
- **Reads / Queries:** Belong in `domain/{domain}/selectors/{model}.py`.
- Keep serializers purely for data shape and views purely for HTTP routing. Never put deep business rules in the DRF layer.
