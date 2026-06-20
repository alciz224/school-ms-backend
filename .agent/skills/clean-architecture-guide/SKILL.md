---
name: Clean Architecture & Implementation Patterns
description: The definitive guide to the DDD (Domain-Driven Design) architecture used in this project. Read this to understand how to correctly distribute logic between models, services, selectors, and API views.
---

# Clean Architecture & Implementation Patterns

This project uses a strict, layered architecture inspired by Domain-Driven Design (DDD). Logic must be cleanly separated into distinct layers. **Never mix database queries into the API layer or put HTTP context into the business logic layer.**

## 1. Directory Structure per Domain
Every domain (e.g., `domain/academic/`, `domain/enrollment/`) must follow this exact structure:
```
domain/{domain_name}/
├── models/           # Database schemas and basic data integrity
├── services/         # All WRITE operations and business rules (Creates, Updates, Deletes)
├── selectors/        # All READ operations and complex queries (Gets, Searches)
├── api/
│   ├── serializers/  # Data shaping for HTTP requests/responses
│   ├── views/        # Thin HTTP routing layer
│   └── urls.py       # DRF Router configuration
├── admin.py          # Django Admin registration
├── constants.py      # Status choices, Enums
└── validators.py     # Custom model validators
```
*Note: Always remember to export your classes in the respective `__init__.py` files for each directory.*

## 2. Models Layer (`models/`)
- **Responsibility:** Data structure, relationships, and basic data integrity.
- **Rules:**
  - Inherit from `domain.shared.models.base.AuditModel`.
  - Put basic validation in the `clean()` method.
  - Override `save()` to call `self.full_clean()` before `super().save()`.
  - Do NOT put complex cross-model business logic here.

## 3. Services Layer (`services/`)
- **Responsibility:** All **WRITE** operations (creation, modification, state changes, deletion).
- **Rules:**
  - Use class-based namespaces with `@staticmethod` for all methods.
  - **Always use keyword-only arguments** (enforced via `*,` as the first parameter).
  - Pass the `user` object explicitly for audit tracking (`created_by`, `updated_by`).
  - Use `@transaction.atomic` for multi-step operations.
  - Raise `DomainException` subclasses from `domain.shared.exceptions` on failure.
```python
class AcademicYearService:
    @staticmethod
    def create(*, code: str, start_year: int, end_year: int, user=None) -> AcademicYear:
        # Business logic goes here
        obj = AcademicYear(code=code, start_year=start_year, end_year=end_year)
        obj.save_by(user=user)
        return obj
```

## 4. Selectors Layer (`selectors/`)
- **Responsibility:** All **READ** operations (fetching, filtering, searching, existence checks).
- **Rules:**
  - Use class-based namespaces with `@staticmethod` for all methods.
  - **Always use keyword-only arguments**.
  - Return `QuerySet[Model]` (for lists) or `Optional[Model]` (for single objects).
  - Encapsulate complex ORM lookups, annotations, and filtering here.
```python
class AcademicYearSelector:
    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[AcademicYear]:
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(code__iexact=code.strip()).first()
```

## 5. API Layer (`api/views/` and `api/serializers/`)
- **Responsibility:** Translate HTTP requests to Domain calls, and Domain responses to HTTP responses.
- **Rules:**
  - **Keep Views Thin:** A ViewSet method should simply grab data from `request.data`, pass it to a Service/Selector, and return the serialized result.
  - **No Business Logic:** Never perform raw `.save()`, `.create()`, or complex `Q()` filtering directly in a View or Serializer.
  - Override `get_queryset()` in ViewSets to call a Selector (e.g., `return MyModelSelector.get_all()`).
  - Perform actions using `@action` decorators and delegate the actual work to a Service.

## 6. General Best Practices
- **Explicit over Implicit:** Never rely on signals for core business logic; write the logic explicitly in the Service method.
- **Soft Deletion:** Always prefer soft deletion (using `obj.soft_delete(user=user)`) over hard deletion. Services should define a `delete` method that accepts a `hard: bool = False` flag.
- **Test in Isolation:** Because the layers are strictly separated, you can unit-test Services and Selectors directly without mocking HTTP requests.
