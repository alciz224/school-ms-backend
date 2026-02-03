# Domain Model Implementation Guide

**Complete Pattern Reference for Django DDD Implementation**

This guide extracts the exact patterns used across all existing domain implementations (academic, geography, school_operations) to ensure 100% consistency for any new model implementation.

---

## Table of Contents

1. [File Structure Pattern](#1-file-structure-pattern)
2. [Code Organization Pattern](#2-code-organization-pattern)
3. [Naming Conventions](#3-naming-conventions)
4. [Import Patterns](#4-import-patterns)
5. [Model Implementation Pattern](#5-model-implementation-pattern)
6. [Service Implementation Pattern](#6-service-implementation-pattern)
7. [Selector Implementation Pattern](#7-selector-implementation-pattern)
8. [API Serializer Pattern](#8-api-serializer-pattern)
9. [API ViewSet Pattern](#9-api-viewset-pattern)
10. [Admin Interface Pattern](#10-admin-interface-pattern)
11. [Constants Pattern](#11-constants-pattern)
12. [Validators Pattern](#12-validators-pattern)
13. [URL Configuration Pattern](#13-url-configuration-pattern)
14. [Test Structure Pattern](#14-test-structure-pattern)
15. [Complete Implementation Checklist](#15-complete-implementation-checklist)

---

## 1. File Structure Pattern

### 1.1 Domain Directory Structure

For a domain named `{domain}` with models `{ModelA}`, `{ModelB}`:

```
domain/{domain}/
├── __init__.py
├── admin.py                          # Admin configuration for ALL models
├── apps.py                           # Django app configuration
├── constants.py                      # Domain-wide constants
├── validators.py                     # Domain-wide validators (optional)
├── signals.py                        # Domain signals (optional)
├── models.py                         # Legacy/empty file (don't use)
├── tests.py                          # Legacy/empty file (don't use)
├── views.py                          # Legacy/empty file (don't use)
│
├── models/
│   ├── __init__.py                   # Export all models
│   ├── base.py                       # Base model for domain (optional)
│   ├── model_a.py                    # One file per model
│   └── model_b.py
│
├── services/
│   ├── __init__.py                   # Export all services
│   ├── model_a.py                    # One service per model
│   └── model_b.py
│
├── selectors/
│   ├── __init__.py                   # Export all selectors
│   ├── model_a.py                    # One selector per model
│   └── model_b.py
│
├── api/
│   ├── __init__.py
│   ├── permissions.py                # Domain-specific permissions
│   ├── urls.py                       # URL routing configuration
│   │
│   ├── serializers/
│   │   ├── __init__.py               # Export all serializers
│   │   ├── model_a.py                # One serializer file per model
│   │   └── model_b.py
│   │
│   └── views/
│       ├── __init__.py               # Export all viewsets
│       ├── model_a.py                # One viewset file per model
│       └── model_b.py
│
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_{domain}.py          # Seeding command (optional)
│
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py                   # Pytest fixtures (optional)
    ├── test_models.py                # Model tests
    ├── test_services.py              # Service tests (optional)
    ├── test_api_{model_a}.py         # API tests per model (optional)
    └── test_urls_contract.py         # URL contract tests (optional)
```

### 1.2 File Naming Conventions

- **Models**: `{model_name_snake_case}.py` (e.g., `academic_year.py`, `school_year.py`)
- **Services**: `{model_name_snake_case}.py` (matches model file name)
- **Selectors**: `{model_name_snake_case}.py` (matches model file name)
- **Serializers**: `{model_name_snake_case}.py` (matches model file name)
- **Views**: `{model_name_snake_case}.py` (matches model file name)
- **Tests**: `test_{model_name_snake_case}.py` or `test_{category}.py`

### 1.3 Required vs Optional Files

**Always Required:**
- `models/{model}.py`
- `services/{model}.py`
- `selectors/{model}.py`
- `api/serializers/{model}.py`
- `api/views/{model}.py`
- `admin.py` (register model)
- All `__init__.py` files with proper exports

**Optional (create when needed):**
- `validators.py` (if model has custom validators)
- `constants.py` (if model needs status/choice constants)
- `signals.py` (if model needs signal handlers)
- `management/commands/seed_{domain}.py` (for data seeding)
- `tests/test_api_{model}.py` (specific API tests)

---

## 2. Code Organization Pattern

### 2.1 Model File Structure Template

```python
"""
{Model} model for {purpose}.
"""

# Standard library imports
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Local imports
from domain.shared.models.base import AuditModel
from domain.shared.models.managers import BaseManager
from ..constants import {ModelStatus}  # If applicable
from ..validators import validate_{something}  # If applicable


# Custom Manager (if needed)
class {Model}Manager(BaseManager):
    """Custom manager for {Model} model."""
    
    def custom_method(self):
        """Custom query method."""
        return self.filter(...)


# Model Class
class {Model}(AuditModel):
    """
    {Brief description}.
    
    {Detailed description of what this model represents}
    
    Business Rules:
        - Rule 1
        - Rule 2
        - Rule 3
    
    Attributes:
        field1: Description
        field2: Description
    """
    
    # Field definitions (grouped logically)
    # 1. Identity/Core fields (code, name, etc.)
    # 2. Foreign keys
    # 3. Data fields
    # 4. Status/Boolean flags
    # 5. Metadata fields
    # Note: Timestamps inherited from AuditModel
    
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_("Unique code"),
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Display name"),
    )
    
    # Custom manager
    objects = {Model}Manager()
    
    class Meta:
        db_table = "{model_snake_case}"
        verbose_name = _("{Model Verbose}")
        verbose_name_plural = _("{Model Verbose Plural}")
        ordering = ["{default_ordering}"]
        indexes = [
            models.Index(fields=["field1"], name="{table}_field1_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_{table}_code",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate model fields."""
        super().clean()
        # Custom validation logic
    
    def save(self, *args, **kwargs):
        """Save with validation."""
        # Pre-save logic (e.g., auto-generate code)
        super().save(*args, **kwargs)
    
    # Property methods
    @property
    def computed_property(self) -> type:
        """Description of property."""
        return self.field
    
    # Business logic methods
    def business_action(self, user=None):
        """
        Perform business action.
        
        Args:
            user: User performing action
        """
        pass
```

### 2.2 Service File Structure Template

```python
"""
{Model} service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from domain.{domain}.models import {Model}
from domain.{domain}.constants import {ModelStatus}  # If applicable


class {Model}Service:
    """Service for {model} operations."""
    
    @staticmethod
    def create(*, field1: type, field2: type = None, user=None) -> {Model}:
        """
        Create a new {model}.
        
        Args:
            field1: Description
            field2: Description (optional)
            user: User performing the action
        
        Returns:
            Created {Model} instance
        
        Raises:
            ValidationError: If validation fails
        """
        obj = {Model}(
            field1=field1,
            field2=field2,
            created_by=user
        )
        obj.save()
        return obj
    
    @staticmethod
    def update(*, obj: {Model}, field1: type = None, user=None) -> {Model}:
        """
        Update a {model}.
        
        Args:
            obj: {Model} instance to update
            field1: New value (optional)
            user: User performing the action
        
        Returns:
            Updated {Model} instance
        """
        if field1 is not None:
            obj.field1 = field1
        
        obj.updated_by = user
        obj.save()
        return obj
    
    @staticmethod
    def delete(*, obj: {Model}, user=None, hard: bool = False) -> None:
        """
        Delete a {model} (soft delete by default).
        
        Args:
            obj: {Model} instance to delete
            user: User performing the action
            hard: If True, permanently delete
        
        Raises:
            ValidationError: If object has dependencies
        """
        # Check for dependencies
        if obj.related_objects.filter(is_deleted=False).exists():
            raise ValidationError(
                _("Cannot delete {model} with related objects.")
            )
        
        if hard:
            obj.hard_delete()
        else:
            obj.deleted_by = user
            obj.delete()  # Uses soft delete from AuditModel
    
    @staticmethod
    def restore(*, obj: {Model}, user=None) -> {Model}:
        """
        Restore a soft-deleted {model}.
        
        Args:
            obj: {Model} instance to restore
            user: User performing the action
        
        Returns:
            Restored {Model} instance
        """
        obj.is_deleted = False
        obj.deleted_at = None
        obj.deleted_by = None
        obj.updated_by = user
        obj.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        return obj
```

### 2.3 Selector File Structure Template

```python
"""
{Model} selectors.
"""

from django.db.models import QuerySet, Q, Count
from typing import Optional

from domain.{domain}.models import {Model}


class {Model}Selector:
    """Selector for {model} queries."""
    
    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[{Model}]:
        """
        Get all {models}.
        
        Args:
            include_deleted: If True, include soft-deleted objects
        
        Returns:
            QuerySet of {models}
        """
        if include_deleted:
            return {Model}.all_objects.all()
        return {Model}.objects.all()
    
    @staticmethod
    def get_by_id(*, obj_id: int, include_deleted: bool = False) -> Optional[{Model}]:
        """
        Get a {model} by ID.
        
        Args:
            obj_id: {Model} ID
            include_deleted: If True, include soft-deleted objects
        
        Returns:
            {Model} instance or None
        """
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(id=obj_id).first()
    
    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[{Model}]:
        """
        Get a {model} by code.
        
        Args:
            code: {Model} code
            include_deleted: If True, include soft-deleted objects
        
        Returns:
            {Model} instance or None
        """
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(code__iexact=code.strip()).first()
    
    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[{Model}]:
        """
        Search {models} by name or code.
        
        Args:
            query: Search query
            include_deleted: If True, include soft-deleted objects
        
        Returns:
            QuerySet of matching {models}
        """
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )
    
    @staticmethod
    def exists_by_code(*, code: str, exclude_id: int = None) -> bool:
        """
        Check if a {model} exists with the given code.
        
        Args:
            code: Code to check
            exclude_id: Exclude object with this ID
        
        Returns:
            True if {model} exists with the code
        """
        queryset = {Model}.objects.filter(code__iexact=code.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        return queryset.exists()
```

---


## 3. Naming Conventions

### 3.1 Python/Django Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Model class | PascalCase | `AcademicYear`, `SchoolYear`, `Country` |
| Model file | snake_case | `academic_year.py`, `school_year.py` |
| Service class | `{Model}Service` | `AcademicYearService` |
| Selector class | `{Model}Selector` | `AcademicYearSelector` |
| Manager class | `{Model}Manager` | `AcademicYearManager` |
| Serializer class | `{Model}Serializer` | `AcademicYearSerializer` |
| ViewSet class | `{Model}ViewSet` | `AcademicYearViewSet` |
| Constants class | PascalCase | `SchoolStatus`, `SchoolType` |
| Validator function | `validate_{purpose}` | `validate_school_code` |
| Service methods | snake_case | `create`, `update`, `delete`, `restore` |
| Selector methods | `get_{purpose}` | `get_all`, `get_by_id`, `get_current` |
| Model methods | snake_case | `activate`, `archive`, `can_be_deleted` |
| Model properties | snake_case | `is_operational`, `full_path` |

### 3.2 Database Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Table name | snake_case | `academic_year`, `school_year` |
| Field name | snake_case | `start_year`, `is_current` |
| Index name | `{table}_{field}_idx` | `academic_year_status_idx` |
| Constraint name | `{type}_{table}_{field}` | `unique_academic_year_code` |
| Foreign key | `{related_model}_id` | `academic_year_id` |
| Related name | `{plural_model}` | `schools`, `levels` |

### 3.3 API Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| URL pattern | kebab-case | `academic-years`, `school-years` |
| Router basename | kebab-case | `academic-year`, `school-year` |
| App namespace | lowercase | `academic`, `geography` |
| Custom action | snake_case | `set_current`, `activate` |
| Query parameter | snake_case | `include_deleted`, `search` |

### 3.4 Import Conventions

**Always use full names - NO aliases:**

```python
# ✓ Correct
from domain.academic.models import AcademicYear
from domain.academic.services import AcademicYearService
from domain.academic.selectors import AcademicYearSelector

# ✗ Wrong
from domain.academic.models import AcademicYear as AY
```

---

## 4. Import Patterns

### 4.1 Model File Imports

```python
"""Model file imports - in this exact order."""

# 1. Standard library imports
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# 2. Third-party imports (if needed)
# (none typically)

# 3. Local domain imports
from domain.shared.models.base import AuditModel
from domain.shared.models.managers import BaseManager
from domain.shared.models.mixins import SomeMixin  # If needed

# 4. Relative imports within domain
from ..constants import ModelStatus
from ..validators import validate_something
```

### 4.2 Service File Imports

```python
"""Service file imports - in this exact order."""

# 1. Standard library
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

# 2. Local domain imports
from domain.{domain}.models import Model
from domain.{domain}.constants import ModelStatus
```

### 4.3 Selector File Imports

```python
"""Selector file imports - in this exact order."""

# 1. Standard library
from django.db.models import QuerySet, Q, Count, F, Prefetch
from typing import Optional

# 2. Local domain imports
from domain.{domain}.models import Model
from domain.{domain}.constants import ModelStatus  # If needed
```

### 4.4 Serializer File Imports

```python
"""Serializer file imports - in this exact order."""

# 1. Third-party
from rest_framework import serializers

# 2. Local domain imports
from domain.{domain}.models import Model
```

### 4.5 ViewSet File Imports

```python
"""ViewSet file imports - in this exact order."""

# 1. Third-party
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# 2. Local domain imports
from domain.{domain}.models import Model
from domain.{domain}.services import ModelService
from domain.{domain}.selectors import ModelSelector
from domain.{domain}.api.serializers import ModelSerializer
from domain.{domain}.api.permissions import IsAdminOrReadOnly
```

### 4.6 __init__.py Export Pattern

**Models __init__.py:**
```python
"""Domain models."""

from domain.{domain}.models.model_a import ModelA
from domain.{domain}.models.model_b import ModelB

__all__ = [
    "ModelA",
    "ModelB",
]
```

**Services __init__.py:**
```python
"""Domain services."""

from .model_a import ModelAService
from .model_b import ModelBService

__all__ = [
    "ModelAService",
    "ModelBService",
]
```

**Selectors __init__.py:**
```python
"""Domain selectors."""

from .model_a import ModelASelector
from .model_b import ModelBSelector

__all__ = [
    "ModelASelector",
    "ModelBSelector",
]
```

**API Serializers __init__.py:**
```python
"""Serializers for Domain API."""

from domain.{domain}.api.serializers.model_a import ModelASerializer
from domain.{domain}.api.serializers.model_b import ModelBSerializer

__all__ = [
    "ModelASerializer",
    "ModelBSerializer",
]
```

**API Views __init__.py:**
```python
"""Views for Domain API."""

from domain.{domain}.api.views.model_a import ModelAViewSet
from domain.{domain}.api.views.model_b import ModelBViewSet

__all__ = [
    "ModelAViewSet",
    "ModelBViewSet",
]
```

---

## 5. Model Implementation Pattern

### 5.1 Base Model Selection

**Use `AuditModel` for all business entities:**

```python
from domain.shared.models.base import AuditModel

class MyModel(AuditModel):
    pass
```

**AuditModel provides:**
- `created_at`, `updated_at` (timestamps)
- `created_by`, `updated_by`, `deleted_by` (user tracking)
- `is_deleted`, `deleted_at` (soft delete)
- `is_active` (activation flag)
- Managers: `objects`, `active`, `deleted`, `inactive`, `all_objects`
- Methods: `save_by()`, `soft_delete()`, `hard_delete()`, `restore()`

### 5.2 Field Definition Pattern

**Field ordering:**
1. Identity fields (code, name)
2. Foreign keys
3. Data fields
4. Status/Boolean fields
5. JSON/metadata fields

**Field pattern:**
```python
field_name = models.FieldType(
    max_length=100,              # Required for CharField
    unique=True,                 # If unique
    blank=True,                  # If optional in forms
    null=True,                   # If optional in DB
    default=value,               # If has default
    choices=ConstantClass.CHOICES,  # If choices
    db_index=True,               # If frequently queried
    validators=[validate_func],  # If custom validation
    help_text=_("Description"),  # Always include
    verbose_name=_("Label"),     # Optional, for forms
)
```

### 5.3 Meta Class Pattern

```python
class Meta:
    db_table = "model_snake_case"
    verbose_name = _("Model Name")
    verbose_name_plural = _("Model Names")
    ordering = ["field"]  # Default ordering
    indexes = [
        models.Index(fields=["field1"], name="table_field1_idx"),
        models.Index(fields=["field1", "field2"], name="table_field1_field2_idx"),
    ]
    constraints = [
        models.UniqueConstraint(
            fields=["code"],
            condition=models.Q(is_deleted=False),
            name="unique_table_code",
        ),
        models.CheckConstraint(
            condition=models.Q(capacity__gt=0),
            name="positive_capacity",
        ),
    ]
```

### 5.4 Custom Manager Pattern

```python
class ModelManager(BaseManager):
    """Custom manager for Model."""
    
    def get_current(self):
        """Get the current instance."""
        return self.filter(is_current=True).first()
    
    def by_status(self, status):
        """Filter by status."""
        return self.filter(status=status, is_deleted=False)
```

### 5.5 Model Methods Pattern

**Always include:**

```python
def __str__(self) -> str:
    """String representation."""
    return f"{self.name} ({self.code})"

def clean(self):
    """Validate model fields."""
    super().clean()
    # Custom validation logic
    if self.field1 > self.field2:
        raise ValidationError({"field1": "Must be less than field2"})

def save(self, *args, **kwargs):
    """Save with validation."""
    # Pre-save logic (auto-generate code, etc.)
    if not self.code:
        self.code = self._generate_code()
    
    # Always call full_clean() unless explicitly skipped
    if not kwargs.pop('skip_validation', False):
        self.full_clean()
    
    super().save(*args, **kwargs)
```

**Business logic methods:**

```python
def activate(self, user=None):
    """Activate this instance."""
    if self.status != Status.DRAFT:
        raise ValidationError("Only draft items can be activated")
    
    self.status = Status.ACTIVE
    self.save_by(user=user)

@property
def is_operational(self) -> bool:
    """Check if operational."""
    return self.status == Status.ACTIVE and not self.is_deleted
```

### 5.6 Foreign Key Pattern

```python
# Standard foreign key
related_model = models.ForeignKey(
    RelatedModel,
    on_delete=models.PROTECT,      # Use PROTECT for references
    related_name="{plural_this_model}",
    verbose_name=_("Related Model"),
    help_text=_("Description"),
)

# Optional foreign key
optional_related = models.ForeignKey(
    RelatedModel,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="{plural_this_model}",
    verbose_name=_("Optional Related"),
)

# User foreign keys (for audit)
created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="+",  # Disable reverse relation
    editable=False,
)
```

---

## 6. Service Implementation Pattern

### 6.1 Service Class Structure

```python
class ModelService:
    """Service for model operations."""
    
    # All methods are @staticmethod
    # Use keyword-only arguments (*, arg1, arg2)
    # Always include user parameter for audit
    # Return the model instance or None
    # Raise ValidationError for business rule violations
```

### 6.2 Standard CRUD Methods

**Create:**
```python
@staticmethod
def create(*, field1: type, field2: type = None, user=None) -> Model:
    """
    Create a new model.
    
    Args:
        field1: Required field description
        field2: Optional field description
        user: User performing the action
    
    Returns:
        Created Model instance
    
    Raises:
        ValidationError: If validation fails
    """
    obj = Model(
        field1=field1,
        field2=field2,
        created_by=user
    )
    obj.save()  # Uses model's save() which calls full_clean()
    return obj
```

**Update:**
```python
@staticmethod
def update(*, obj: Model, field1: type = None, field2: type = None, 
           user=None) -> Model:
    """
    Update a model.
    
    Args:
        obj: Model instance to update
        field1: New value (optional)
        field2: New value (optional)
        user: User performing the action
    
    Returns:
        Updated Model instance
    """
    if field1 is not None:
        obj.field1 = field1
    if field2 is not None:
        obj.field2 = field2
    
    obj.updated_by = user
    obj.save()  # Full validation
    return obj
```

**Delete:**
```python
@staticmethod
def delete(*, obj: Model, user=None, hard: bool = False) -> None:
    """
    Delete a model (soft delete by default).
    
    Args:
        obj: Model instance to delete
        user: User performing the action
        hard: If True, permanently delete
    
    Raises:
        ValidationError: If object has dependencies
    """
    # Always check for dependencies
    if obj.related_set.filter(is_deleted=False).exists():
        raise ValidationError(
            _("Cannot delete model with related objects. "
              "Delete or reassign related objects first.")
        )
    
    if hard:
        obj.hard_delete()
    else:
        obj.deleted_by = user
        obj.delete()  # Soft delete from AuditModel
```

**Restore:**
```python
@staticmethod
def restore(*, obj: Model, user=None) -> Model:
    """
    Restore a soft-deleted model.
    
    Args:
        obj: Model instance to restore
        user: User performing the action
    
    Returns:
        Restored Model instance
    """
    obj.is_deleted = False
    obj.deleted_at = None
    obj.deleted_by = None
    obj.updated_by = user
    obj.save(update_fields=[
        "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
    ])
    return obj
```

### 6.3 Business Action Methods

```python
@staticmethod
def activate(*, obj: Model, user=None) -> Model:
    """
    Activate a model.
    
    Args:
        obj: Model instance to activate
        user: User performing the action
    
    Returns:
        Updated Model instance
    
    Raises:
        ValidationError: If cannot be activated
    """
    if obj.status != Status.DRAFT:
        raise ValidationError(
            _("Only draft items can be activated")
        )
    
    obj.status = Status.ACTIVE
    obj.updated_by = user
    obj.save(update_fields=["status", "updated_at", "updated_by"])
    return obj

@staticmethod
@transaction.atomic
def complex_operation(*, obj: Model, param: type, user=None) -> Model:
    """
    Perform complex operation (use transaction.atomic if needed).
    
    Args:
        obj: Model instance
        param: Parameter description
        user: User performing the action
    
    Returns:
        Updated Model instance
    """
    # Multiple operations that should be atomic
    obj.field = param
    obj.save()
    
    # Related operations
    RelatedModel.objects.create(parent=obj)
    
    return obj
```

---

## 7. Selector Implementation Pattern

### 7.1 Selector Class Structure

```python
class ModelSelector:
    """Selector for model queries."""
    
    # All methods are @staticmethod
    # Use keyword-only arguments (*, arg1, arg2)
    # Return QuerySet or Optional[Model]
    # Never modify data - read-only operations
    # Include include_deleted parameter for soft-deleted items
```

### 7.2 Standard Query Methods

**Get all:**
```python
@staticmethod
def get_all(*, include_deleted: bool = False) -> QuerySet[Model]:
    """
    Get all models.
    
    Args:
        include_deleted: If True, include soft-deleted objects
    
    Returns:
        QuerySet of models
    """
    if include_deleted:
        return Model.all_objects.all()
    return Model.objects.all()
```

**Get by ID:**
```python
@staticmethod
def get_by_id(*, obj_id: int, include_deleted: bool = False) -> Optional[Model]:
    """
    Get a model by ID.
    
    Args:
        obj_id: Model ID
        include_deleted: If True, include soft-deleted objects
    
    Returns:
        Model instance or None
    """
    manager = Model.all_objects if include_deleted else Model.objects
    return manager.filter(id=obj_id).first()
```

**Get by unique field:**
```python
@staticmethod
def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[Model]:
    """
    Get a model by code.
    
    Args:
        code: Model code
        include_deleted: If True, include soft-deleted objects
    
    Returns:
        Model instance or None
    """
    manager = Model.all_objects if include_deleted else Model.objects
    return manager.filter(code__iexact=code.strip()).first()
```

**Search:**
```python
@staticmethod
def search(*, query: str, include_deleted: bool = False) -> QuerySet[Model]:
    """
    Search models by name or code.
    
    Args:
        query: Search query
        include_deleted: If True, include soft-deleted objects
    
    Returns:
        QuerySet of matching models
    """
    manager = Model.all_objects if include_deleted else Model.objects
    return manager.filter(
        Q(name__icontains=query) | Q(code__icontains=query)
    )
```

### 7.3 Existence Check Methods

```python
@staticmethod
def exists_by_code(*, code: str, exclude_id: int = None) -> bool:
    """
    Check if a model exists with the given code.
    
    Args:
        code: Code to check
        exclude_id: Exclude object with this ID
    
    Returns:
        True if model exists with the code
    """
    queryset = Model.objects.filter(code__iexact=code.strip())
    
    if exclude_id:
        queryset = queryset.exclude(id=exclude_id)
    
    return queryset.exists()
```

### 7.4 Filter and Annotated Query Methods

```python
@staticmethod
def get_by_status(*, status: str, include_deleted: bool = False) -> QuerySet[Model]:
    """
    Get models by status.
    
    Args:
        status: Model status
        include_deleted: If True, include soft-deleted objects
    
    Returns:
        QuerySet of models with specified status
    """
    manager = Model.all_objects if include_deleted else Model.objects
    return manager.filter(status=status)

@staticmethod
def get_with_counts() -> QuerySet[Model]:
    """
    Get all models with related object counts.
    
    Returns:
        QuerySet of models annotated with counts
    """
    return Model.objects.annotate(
        related_count=Count('related_set', filter=Q(related_set__is_deleted=False))
    )
```

---

## 8. API Serializer Pattern

### 8.1 Simple ModelSerializer Pattern

```python
"""Serializer for Model."""
from rest_framework import serializers

from domain.{domain}.models import Model


class ModelSerializer(serializers.ModelSerializer):
    """Serializer for Model."""
    
    class Meta:
        model = Model
        fields = [
            "id",
            "code",
            "name",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]
    
    def validate(self, attrs):
        """Validate the data."""
        # Custom validation logic
        return attrs
```

### 8.2 Serializer with Computed Fields

```python
class ModelSerializer(serializers.ModelSerializer):
    """Serializer for Model."""
    
    # Computed fields
    computed_field = serializers.SerializerMethodField()
    related_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Model
        fields = [
            "id",
            "code",
            "name",
            "computed_field",
            "related_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_computed_field(self, obj):
        """Get computed field value."""
        return obj.some_property
```

### 8.3 Multiple Serializers Pattern (Geography Pattern)

**For complex APIs, use separate serializers:**

```python
class ModelListSerializer(serializers.ModelSerializer):
    """Serializer for model list view."""
    
    related_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Model
        fields = ['id', 'code', 'name', 'related_count', 'created_at']
        read_only_fields = fields


class ModelDetailSerializer(serializers.ModelSerializer):
    """Serializer for model detail view."""
    
    related_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Model
        fields = [
            'id', 'code', 'name', 'description', 'related_count',
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = fields


class ModelCreateSerializer(serializers.Serializer):
    """Serializer for model creation."""
    
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=100)
    
    def validate_code(self, value):
        """Validate code uniqueness."""
        code = value.upper().strip()
        if Model.objects.filter(code__iexact=code).exists():
            raise serializers.ValidationError('A model with this code already exists.')
        return code


class ModelUpdateSerializer(serializers.Serializer):
    """Serializer for model update."""
    
    code = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=100, required=False)
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)
    
    def validate_code(self, value):
        """Validate code uniqueness."""
        if value is None:
            return value
        code = value.upper().strip()
        queryset = Model.objects.filter(code__iexact=code)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError('A model with this code already exists.')
        return code
```

---

## 9. API ViewSet Pattern

### 9.1 Simple ModelViewSet Pattern (Academic Pattern)

```python
"""ViewSet for Model."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.{domain}.api.permissions import IsAdminOrReadOnly
from domain.{domain}.api.serializers import ModelSerializer
from domain.{domain}.services import ModelService
from domain.{domain}.selectors import ModelSelector


class ModelViewSet(viewsets.ModelViewSet):
    """ViewSet for Model."""
    
    serializer_class = ModelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["status", "is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["code"]
    
    def get_queryset(self):
        """Get queryset using selector."""
        return ModelSelector.get_all()
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a model."""
        obj = self.get_object()
        try:
            obj = ModelService.activate(obj=obj, user=request.user)
            serializer = self.get_serializer(obj)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
```

### 9.2 Advanced ViewSet Pattern (Geography Pattern)

```python
"""Model API views."""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from domain.{domain}.models import Model
from domain.{domain}.services import ModelService
from domain.{domain}.selectors import ModelSelector
from domain.{domain}.api.serializers import (
    ModelListSerializer,
    ModelDetailSerializer,
    ModelCreateSerializer,
    ModelUpdateSerializer,
)
from domain.shared.api.responses import api_response


class ModelViewSet(viewsets.ViewSet):
    """
    ViewSet for Model CRUD operations.
    
    list: GET /api/v1/models/
    create: POST /api/v1/models/
    retrieve: GET /api/v1/models/{id}/
    update: PUT /api/v1/models/{id}/
    partial_update: PATCH /api/v1/models/{id}/
    destroy: DELETE /api/v1/models/{id}/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get base queryset with annotations."""
        return Model.objects.annotate(
            related_count=Count('related_set', filter=Q(related_set__is_deleted=False))
        )
    
    def list(self, request):
        """List all models."""
        queryset = self.get_queryset().order_by('name')
        
        # Optional search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        serializer = ModelListSerializer(queryset, many=True)
        return api_response(data=serializer.data)
    
    def create(self, request):
        """Create a new model."""
        serializer = ModelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        obj = ModelService.create(
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            user=request.user
        )
        
        # Re-fetch with annotations
        obj = self.get_queryset().get(id=obj.id)
        output_serializer = ModelDetailSerializer(obj)
        return api_response(
            data=output_serializer.data,
            message='Model created successfully.',
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, pk=None):
        """Get a model by ID."""
        obj = self.get_queryset().filter(id=pk).first()
        if not obj:
            return api_response(
                success=False,
                message='Model not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ModelDetailSerializer(obj)
        return api_response(data=serializer.data)
    
    def update(self, request, pk=None):
        """Update a model."""
        obj = Model.objects.filter(id=pk).first()
        if not obj:
            return api_response(
                success=False,
                message='Model not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ModelUpdateSerializer(data=request.data, model=obj)
        serializer.is_valid(raise_exception=True)
        
        obj = ModelService.update(
            obj=obj,
            code=serializer.validated_data.get('code'),
            name=serializer.validated_data.get('name'),
            user=request.user
        )
        
        # Re-fetch with annotations
        obj = self.get_queryset().get(id=obj.id)
        output_serializer = ModelDetailSerializer(obj)
        return api_response(
            data=output_serializer.data,
            message='Model updated successfully.'
        )
    
    def partial_update(self, request, pk=None):
        """Partially update a model."""
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """Delete a model (soft delete)."""
        obj = Model.objects.filter(id=pk).first()
        if not obj:
            return api_response(
                success=False,
                message='Model not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            ModelService.delete(obj=obj, user=request.user)
            return api_response(
                message='Model deleted successfully.',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
```

### 9.3 Custom Actions Pattern

```python
@action(detail=False, methods=["get"])
def current(self, request):
    """Get the current model."""
    current_obj = ModelSelector.get_current()
    if current_obj:
        serializer = self.get_serializer(current_obj)
        return Response(serializer.data)
    return Response(
        {"detail": "No current model found"},
        status=status.HTTP_404_NOT_FOUND,
    )

@action(detail=True, methods=["post"])
def custom_action(self, request, pk=None):
    """Custom detail-level action."""
    obj = self.get_object()
    try:
        obj = ModelService.custom_action(obj=obj, user=request.user)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
```

---

## 10. Admin Interface Pattern

### 10.1 Simple Admin Pattern

```python
"""Admin configuration for Domain."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from domain.{domain}.models import Model


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    """Admin configuration for Model."""
    
    list_display = ['code', 'name', 'status', 'is_active', 'created_at']
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'status')
        }),
        (_('Audit'), {
            'fields': (
                'is_active',
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        obj.save_by(user=request.user)
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        obj.soft_delete(user=request.user)
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            obj.soft_delete(user=request.user)
```

### 10.2 Advanced Admin Pattern

```python
@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    """Admin configuration for Model."""
    
    list_display = [
        'code',
        'name',
        'status_display',
        'is_active',
        'related_count',
        'created_at'
    ]
    
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['name']
    
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    
    fieldsets = (
        (_('General Information'), {
            'fields': ('code', 'name', 'status')
        }),
        (_('Audit'), {
            'fields': (
                'is_active',
                'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_items', 'deactivate_items']
    
    def status_display(self, obj):
        """Display status with colored badge."""
        from django.utils.html import format_html
        
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'draft': 'orange',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Status')
    
    def related_count(self, obj):
        """Display related object count."""
        return obj.related_set.filter(is_deleted=False).count()
    related_count.short_description = _('Related Count')
    
    def activate_items(self, request, queryset):
        """Activate selected items."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('%(count)d item(s) activated.') % {'count': updated}
        )
    activate_items.short_description = _('Activate selected items')
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'created_by',
            'updated_by'
        )
    
    def save_model(self, request, obj, form, change):
        """Save model with user tracking."""
        obj.save_by(user=request.user)
    
    def delete_model(self, request, obj):
        """Perform soft delete."""
        obj.soft_delete(user=request.user)
    
    def delete_queryset(self, request, queryset):
        """Perform bulk soft delete."""
        for obj in queryset:
            obj.soft_delete(user=request.user)
```

---

## 11. Constants Pattern

### 11.1 Constants File Structure

```python
"""Constants for Domain."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ModelStatus(models.TextChoices):
    """Status choices for Model."""
    
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ARCHIVED = "archived", _("Archived")


class ModelType(models.TextChoices):
    """Type choices for Model."""
    
    TYPE_A = "type_a", _("Type A")
    TYPE_B = "type_b", _("Type B")
    TYPE_C = "type_c", _("Type C")


# Domain-wide constants
MAX_CODE_LENGTH = 50
MAX_NAME_LENGTH = 200
DEFAULT_PAGE_SIZE = 20
```

### 11.2 Using Constants in Models

```python
from ..constants import ModelStatus, MAX_CODE_LENGTH

class Model(AuditModel):
    status = models.CharField(
        max_length=20,
        choices=ModelStatus.choices,
        default=ModelStatus.DRAFT,
        help_text=_("Model status"),
    )
    
    code = models.CharField(
        max_length=MAX_CODE_LENGTH,
        unique=True,
        help_text=_("Unique code"),
    )
```

---

## 12. Validators Pattern

### 12.1 Validators File Structure

```python
"""Custom validators for Domain."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_code_format(value):
    """
    Validate code format.
    
    Code must be alphanumeric, uppercase, and may contain hyphens.
    
    Args:
        value: Code value to validate
    
    Raises:
        ValidationError: If code format is invalid
    """
    if not re.match(r'^[A-Z0-9-]+$', value):
        raise ValidationError(
            _('Code must contain only uppercase letters, numbers, and hyphens.')
        )


def validate_year_range(value):
    """
    Validate year is within acceptable range.
    
    Args:
        value: Year value to validate
    
    Raises:
        ValidationError: If year is out of range
    """
    current_year = timezone.now().year
    if value < 1900 or value > current_year + 10:
        raise ValidationError(
            _('Year must be between 1900 and %(max_year)s.'),
            params={'max_year': current_year + 10}
        )


def validate_positive(value):
    """
    Validate value is positive.
    
    Args:
        value: Value to validate
    
    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(_('Value must be positive.'))


def validate_unique_code(value, model_class, exclude_id=None):
    """
    Validate code uniqueness across non-deleted instances.
    
    Args:
        value: Code to check
        model_class: Model class to check against
        exclude_id: ID to exclude from check (for updates)
    
    Raises:
        ValidationError: If code already exists
    """
    queryset = model_class.objects.filter(code__iexact=value.strip())
    
    if exclude_id:
        queryset = queryset.exclude(id=exclude_id)
    
    if queryset.exists():
        raise ValidationError(
            _('%(model)s with this code already exists.'),
            params={'model': model_class._meta.verbose_name}
        )
```

### 12.2 Using Validators in Models

```python
from ..validators import validate_code_format, validate_positive

class Model(AuditModel):
    code = models.CharField(
        max_length=50,
        validators=[validate_code_format],
        help_text=_("Unique code"),
    )
    
    capacity = models.IntegerField(
        validators=[validate_positive],
        help_text=_("Maximum capacity"),
    )
```

---

## 13. URL Configuration Pattern

### 13.1 Domain API URLs Pattern

```python
"""URL configuration for Domain API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.{domain}.api.views import (
    ModelAViewSet,
    ModelBViewSet,
    ModelCViewSet,
)

app_name = "{domain}"

router = DefaultRouter()
router.register(r"model-as", ModelAViewSet, basename="model-a")
router.register(r"model-bs", ModelBViewSet, basename="model-b")
router.register(r"model-cs", ModelCViewSet, basename="model-c")

urlpatterns = [
    path("", include(router.urls)),
]
```

### 13.2 URL Naming Conventions

**Router registration:**
- URL pattern: plural, kebab-case (e.g., `academic-years`, `school-years`)
- Basename: singular, kebab-case (e.g., `academic-year`, `school-year`)

**Generated URL names:**
- List: `{domain}:{basename}-list`
- Detail: `{domain}:{basename}-detail`
- Create: `{domain}:{basename}-list` (POST)
- Update: `{domain}:{basename}-detail` (PUT/PATCH)
- Delete: `{domain}:{basename}-detail` (DELETE)
- Custom action: `{domain}:{basename}-{action-name}`

**Examples:**
```python
# academic:academic-year-list
# academic:academic-year-detail
# academic:academic-year-set-current
# geography:country-list
# geography:country-detail
```

### 13.3 Main URLs Integration

In project's main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path("api/v1/academic/", include("domain.academic.api.urls")),
    path("api/v1/geography/", include("domain.geography.api.urls")),
    path("api/v1/school-operations/", include("domain.school_operations.api.urls")),
]
```

---

## 14. Test Structure Pattern

### 14.1 Basic Model Test Pattern

```python
"""Tests for Model."""
import pytest
from django.core.exceptions import ValidationError

from domain.{domain}.models import Model
from domain.{domain}.services import ModelService
from domain.{domain}.selectors import ModelSelector


@pytest.mark.django_db
class TestModel:
    """Tests for Model model."""
    
    def test_create_model(self):
        """Test creating a model."""
        obj = Model.objects.create(
            code="TEST01",
            name="Test Model",
        )
        
        assert obj.id is not None
        assert obj.code == "TEST01"
        assert obj.name == "Test Model"
        assert not obj.is_deleted
    
    def test_str_representation(self):
        """Test string representation."""
        obj = Model.objects.create(
            code="TEST01",
            name="Test Model",
        )
        
        assert str(obj) == "Test Model (TEST01)"
    
    def test_unique_code_constraint(self):
        """Test code uniqueness constraint."""
        Model.objects.create(code="TEST01", name="Test 1")
        
        with pytest.raises(ValidationError):
            Model.objects.create(code="TEST01", name="Test 2")
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        obj.delete()
        
        assert obj.is_deleted
        assert obj.deleted_at is not None
        assert Model.objects.count() == 0
        assert Model.all_objects.count() == 1


@pytest.mark.django_db
class TestModelService:
    """Tests for ModelService."""
    
    def test_create(self):
        """Test creating a model via service."""
        obj = ModelService.create(
            code="TEST01",
            name="Test Model",
        )
        
        assert obj.id is not None
        assert obj.code == "TEST01"
    
    def test_update(self):
        """Test updating a model via service."""
        obj = ModelService.create(code="TEST01", name="Test")
        
        updated = ModelService.update(
            obj=obj,
            name="Updated Name",
        )
        
        assert updated.name == "Updated Name"
        assert updated.code == "TEST01"  # Unchanged
    
    def test_delete_with_dependencies(self):
        """Test delete fails when dependencies exist."""
        obj = ModelService.create(code="TEST01", name="Test")
        # Create related object
        # RelatedModel.objects.create(parent=obj)
        
        # with pytest.raises(ValidationError):
        #     ModelService.delete(obj=obj)
    
    def test_restore(self):
        """Test restoring a soft-deleted model."""
        obj = ModelService.create(code="TEST01", name="Test")
        ModelService.delete(obj=obj)
        
        restored = ModelService.restore(obj=obj)
        
        assert not restored.is_deleted
        assert restored.deleted_at is None


@pytest.mark.django_db
class TestModelSelector:
    """Tests for ModelSelector."""
    
    def test_get_all(self):
        """Test getting all models."""
        Model.objects.create(code="TEST01", name="Test 1")
        Model.objects.create(code="TEST02", name="Test 2")
        
        models = ModelSelector.get_all()
        
        assert models.count() == 2
    
    def test_get_by_id(self):
        """Test getting model by ID."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        found = ModelSelector.get_by_id(obj_id=obj.id)
        
        assert found == obj
    
    def test_get_by_code(self):
        """Test getting model by code."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        found = ModelSelector.get_by_code(code="test01")  # Case-insensitive
        
        assert found == obj
    
    def test_search(self):
        """Test searching models."""
        Model.objects.create(code="TEST01", name="Alpha")
        Model.objects.create(code="TEST02", name="Beta")
        Model.objects.create(code="TEST03", name="Gamma")
        
        results = ModelSelector.search(query="beta")
        
        assert results.count() == 1
        assert results.first().name == "Beta"
    
    def test_exists_by_code(self):
        """Test checking code existence."""
        Model.objects.create(code="TEST01", name="Test")
        
        assert ModelSelector.exists_by_code(code="TEST01")
        assert not ModelSelector.exists_by_code(code="TEST02")
```

### 14.2 API Test Pattern

```python
"""API tests for Model."""
import pytest
from rest_framework.test import APIClient
from rest_framework import status

from domain.{domain}.models import Model


@pytest.mark.django_db
class TestModelAPI:
    """Tests for Model API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_list_models(self):
        """Test listing models."""
        Model.objects.create(code="TEST01", name="Test 1")
        Model.objects.create(code="TEST02", name="Test 2")
        
        response = self.client.get("/api/v1/{domain}/models/")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_create_model(self):
        """Test creating a model via API."""
        data = {
            "code": "TEST01",
            "name": "Test Model",
        }
        
        response = self.client.post("/api/v1/{domain}/models/", data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Model.objects.count() == 1
    
    def test_retrieve_model(self):
        """Test retrieving a model."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        response = self.client.get(f"/api/v1/{domain}/models/{obj.id}/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "TEST01"
    
    def test_update_model(self):
        """Test updating a model via API."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        data = {"name": "Updated Name"}
        response = self.client.patch(f"/api/v1/{domain}/models/{obj.id}/", data)
        
        assert response.status_code == status.HTTP_200_OK
        obj.refresh_from_db()
        assert obj.name == "Updated Name"
    
    def test_delete_model(self):
        """Test deleting a model via API."""
        obj = Model.objects.create(code="TEST01", name="Test")
        
        response = self.client.delete(f"/api/v1/{domain}/models/{obj.id}/")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Model.objects.count() == 0
        assert Model.all_objects.count() == 1  # Soft deleted
```

---

## 15. Complete Implementation Checklist

### 15.1 Pre-Implementation

- [ ] Review domain boundaries and model responsibilities
- [ ] Define model fields and relationships
- [ ] Identify business rules and constraints
- [ ] Plan status/choice constants if needed
- [ ] Design validation rules

### 15.2 Model Implementation

- [ ] Create `models/{model_name}.py`
- [ ] Define model class inheriting from `AuditModel`
- [ ] Add all fields with proper types and constraints
- [ ] Add `Meta` class with `db_table`, `verbose_name`, etc.
- [ ] Add indexes and database constraints
- [ ] Implement `__str__()` method
- [ ] Implement `clean()` validation method
- [ ] Implement `save()` with pre-save logic if needed
- [ ] Add custom manager if needed
- [ ] Add business logic methods and properties
- [ ] Export model in `models/__init__.py`

### 15.3 Service Implementation

- [ ] Create `services/{model_name}.py`
- [ ] Define `{Model}Service` class
- [ ] Implement `create()` method
- [ ] Implement `update()` method
- [ ] Implement `delete()` method with dependency checks
- [ ] Implement `restore()` method
- [ ] Add business action methods (activate, archive, etc.)
- [ ] Use `@transaction.atomic` for complex operations
- [ ] Export service in `services/__init__.py`

### 15.4 Selector Implementation

- [ ] Create `selectors/{model_name}.py`
- [ ] Define `{Model}Selector` class
- [ ] Implement `get_all()` method
- [ ] Implement `get_by_id()` method
- [ ] Implement `get_by_code()` method (if applicable)
- [ ] Implement `search()` method
- [ ] Implement `exists_by_code()` method
- [ ] Add filter methods (`get_by_status()`, etc.)
- [ ] Add annotated query methods if needed
- [ ] Export selector in `selectors/__init__.py`

### 15.5 API Serializer Implementation

- [ ] Create `api/serializers/{model_name}.py`
- [ ] Define serializer class(es)
- [ ] Specify `Meta` with `model`, `fields`, `read_only_fields`
- [ ] Add computed fields with `SerializerMethodField` if needed
- [ ] Add field-level validation methods
- [ ] Add `validate()` method for cross-field validation
- [ ] Export serializer in `api/serializers/__init__.py`

### 15.6 API ViewSet Implementation

- [ ] Create `api/views/{model_name}.py`
- [ ] Define viewset class (`ModelViewSet` or `ViewSet`)
- [ ] Set `serializer_class` and `permission_classes`
- [ ] Implement `get_queryset()` using selector
- [ ] Add filtering, searching, ordering configurations
- [ ] Implement custom actions if needed
- [ ] Use service layer for create/update/delete
- [ ] Export viewset in `api/views/__init__.py`

### 15.7 URL Configuration

- [ ] Register viewset in `api/urls.py`
- [ ] Use appropriate basename (kebab-case, singular)
- [ ] Verify URL patterns (plural, kebab-case)
- [ ] Test URL routing

### 15.8 Admin Interface

- [ ] Register model in `admin.py`
- [ ] Define `ModelAdmin` class
- [ ] Configure `list_display`, `list_filter`, `search_fields`
- [ ] Set `readonly_fields` for audit fields
- [ ] Define `fieldsets` with logical grouping
- [ ] Implement `save_model()` with user tracking
- [ ] Implement `delete_model()` for soft delete
- [ ] Implement `delete_queryset()` for bulk soft delete
- [ ] Add custom display methods if needed
- [ ] Add admin actions if needed

### 15.9 Constants and Validators

- [ ] Add constants to `constants.py` if needed
- [ ] Define `TextChoices` classes for status/type fields
- [ ] Add validators to `validators.py` if needed
- [ ] Implement custom validation functions
- [ ] Use validators in model field definitions

### 15.10 Testing

- [ ] Create test file `tests/test_{model_name}.py`
- [ ] Write model tests (creation, validation, constraints)
- [ ] Write service tests (CRUD operations, business logic)
- [ ] Write selector tests (queries, filters)
- [ ] Write API tests (endpoints, permissions)
- [ ] Achieve good test coverage (aim for >80%)

### 15.11 Documentation

- [ ] Add docstrings to all classes and methods
- [ ] Document business rules in model docstring
- [ ] Document method parameters and return types
- [ ] Add inline comments for complex logic
- [ ] Update domain README if applicable

### 15.12 Migration and Deployment

- [ ] Create migration: `python manage.py makemigrations {domain}`
- [ ] Review migration file for correctness
- [ ] Apply migration: `python manage.py migrate`
- [ ] Test migration rollback if needed
- [ ] Add seed data command if applicable
- [ ] Update API documentation

### 15.13 Final Verification

- [ ] Run all tests: `pytest`
- [ ] Check code style: `flake8`, `black`, `isort`
- [ ] Verify admin interface works correctly
- [ ] Test API endpoints with Postman/curl
- [ ] Verify soft delete works properly
- [ ] Check audit trail functionality
- [ ] Verify permissions work as expected
- [ ] Test with realistic data

---

## Quick Reference: File Templates

### Model Template (models/{model}.py)
```python
"""Model for {purpose}."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from domain.shared.models.base import AuditModel

class {Model}(AuditModel):
    """Model description."""
    
    code = models.CharField(max_length=50, unique=True, help_text=_("Code"))
    name = models.CharField(max_length=200, help_text=_("Name"))
    
    class Meta:
        db_table = "{model_snake}"
        verbose_name = _("{Model}")
        verbose_name_plural = _("{Models}")
        ordering = ["name"]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
```

### Service Template (services/{model}.py)
```python
"""Service for {Model}."""
from domain.{domain}.models import {Model}

class {Model}Service:
    """Service for {model} operations."""
    
    @staticmethod
    def create(*, code: str, name: str, user=None) -> {Model}:
        """Create a new {model}."""
        obj = {Model}(code=code, name=name, created_by=user)
        obj.save()
        return obj
    
    @staticmethod
    def update(*, obj: {Model}, name: str = None, user=None) -> {Model}:
        """Update a {model}."""
        if name is not None:
            obj.name = name
        obj.updated_by = user
        obj.save()
        return obj
    
    @staticmethod
    def delete(*, obj: {Model}, user=None, hard: bool = False) -> None:
        """Delete a {model}."""
        if hard:
            obj.hard_delete()
        else:
            obj.deleted_by = user
            obj.delete()
```

### Selector Template (selectors/{model}.py)
```python
"""Selectors for {Model}."""
from django.db.models import QuerySet
from typing import Optional
from domain.{domain}.models import {Model}

class {Model}Selector:
    """Selector for {model} queries."""
    
    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[{Model}]:
        """Get all {models}."""
        return {Model}.all_objects.all() if include_deleted else {Model}.objects.all()
    
    @staticmethod
    def get_by_id(*, obj_id: int, include_deleted: bool = False) -> Optional[{Model}]:
        """Get {model} by ID."""
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(id=obj_id).first()
    
    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[{Model}]:
        """Get {model} by code."""
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(code__iexact=code.strip()).first()
```

### Serializer Template (api/serializers/{model}.py)
```python
"""Serializer for {Model}."""
from rest_framework import serializers
from domain.{domain}.models import {Model}

class {Model}Serializer(serializers.ModelSerializer):
    """Serializer for {Model}."""
    
    class Meta:
        model = {Model}
        fields = ["id", "code", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
```

### ViewSet Template (api/views/{model}.py)
```python
"""ViewSet for {Model}."""
from rest_framework import viewsets
from domain.{domain}.models import {Model}
from domain.{domain}.api.serializers import {Model}Serializer
from domain.{domain}.selectors import {Model}Selector

class {Model}ViewSet(viewsets.ModelViewSet):
    """ViewSet for {Model}."""
    
    serializer_class = {Model}Serializer
    
    def get_queryset(self):
        """Get queryset using selector."""
        return {Model}Selector.get_all()
```

---

## Summary

This guide provides a complete, consistent pattern for implementing domain models in this Django DDD project. By following these patterns exactly, you ensure:

1. **Consistency**: All models follow the same structure and conventions
2. **Maintainability**: Clear separation of concerns and predictable organization
3. **Testability**: Isolated business logic in services makes testing easier
4. **Scalability**: Clean architecture supports growth and changes
5. **Team Alignment**: Everyone follows the same patterns and standards

**Key Principles:**
- Models contain data structure and basic validation
- Services contain business logic and write operations
- Selectors contain query logic and read operations
- API layer is thin and delegates to services/selectors
- Always use soft delete (is_deleted flag)
- Always track user actions (created_by, updated_by, deleted_by)
- Always use keyword-only arguments in services/selectors
- Always use static methods in services/selectors
- Always validate data before saving
- Always check dependencies before deleting

**When implementing a new model, follow this guide step-by-step and use the checklist in section 15 to ensure nothing is missed.**
