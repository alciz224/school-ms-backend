# Domain Model Implementation Quick Reference

**One-page reference for implementing new domain models**

> For complete details, see [DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)

---

## File Structure

```
domain/{domain}/
├── models/{model}.py          → Model class
├── services/{model}.py        → Business logic (create, update, delete)
├── selectors/{model}.py       → Query logic (get, search, filter)
├── api/serializers/{model}.py → API serialization
├── api/views/{model}.py       → API endpoints
├── admin.py                   → Register admin (all models)
├── constants.py               → Status choices, constants
└── validators.py              → Custom validators
```

**Don't forget**: Update all `__init__.py` files with exports!

---

## Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Model class | `PascalCase` | `AcademicYear` |
| Files | `snake_case.py` | `academic_year.py` |
| Service class | `{Model}Service` | `AcademicYearService` |
| Selector class | `{Model}Selector` | `AcademicYearSelector` |
| Table name | `snake_case` | `academic_year` |
| URL pattern | `kebab-case` (plural) | `academic-years` |
| Router basename | `kebab-case` (singular) | `academic-year` |

---

## Model Template

```python
"""Model for {purpose}."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from domain.shared.models.base import AuditModel

class {Model}(AuditModel):
    """
    {Description}
    
    Business Rules:
        - Rule 1
        - Rule 2
    """
    
    # Identity fields
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    
    # Custom manager (optional)
    # objects = {Model}Manager()
    
    class Meta:
        db_table = "{model_snake}"
        verbose_name = _("{Model}")
        verbose_name_plural = _("{Models}")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_{table}_code",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
```

---

## Service Template

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
        """Delete a {model} (soft delete by default)."""
        # Check dependencies first!
        if hard:
            obj.hard_delete()
        else:
            obj.deleted_by = user
            obj.delete()
    
    @staticmethod
    def restore(*, obj: {Model}, user=None) -> {Model}:
        """Restore a soft-deleted {model}."""
        obj.is_deleted = False
        obj.deleted_at = None
        obj.deleted_by = None
        obj.updated_by = user
        obj.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        return obj
```

---

## Selector Template

```python
"""Selectors for {Model}."""
from django.db.models import QuerySet, Q
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
    
    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[{Model}]:
        """Search {models}."""
        manager = {Model}.all_objects if include_deleted else {Model}.objects
        return manager.filter(Q(name__icontains=query) | Q(code__icontains=query))
    
    @staticmethod
    def exists_by_code(*, code: str, exclude_id: int = None) -> bool:
        """Check if {model} exists with code."""
        queryset = {Model}.objects.filter(code__iexact=code.strip())
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()
```

---

## Serializer Template

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

---

## ViewSet Template

```python
"""ViewSet for {Model}."""
from rest_framework import viewsets
from domain.{domain}.api.serializers import {Model}Serializer
from domain.{domain}.selectors import {Model}Selector

class {Model}ViewSet(viewsets.ModelViewSet):
    """ViewSet for {Model}."""
    
    serializer_class = {Model}Serializer
    filterset_fields = ["status", "is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    
    def get_queryset(self):
        """Get queryset using selector."""
        return {Model}Selector.get_all()
```

---

## Admin Template

```python
"""Admin for {domain}."""
from django.contrib import admin
from domain.{domain}.models import {Model}

@admin.register({Model})
class {Model}Admin(admin.ModelAdmin):
    """Admin for {Model}."""
    
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['name']
    readonly_fields = [
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'is_deleted', 'deleted_at', 'deleted_by'
    ]
    
    fieldsets = (
        (None, {'fields': ('code', 'name')}),
        ('Audit', {
            'fields': (
                'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by',
                'is_deleted', 'deleted_at', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Save with user tracking."""
        obj.save_by(user=request.user)
    
    def delete_model(self, request, obj):
        """Soft delete."""
        obj.soft_delete(user=request.user)
    
    def delete_queryset(self, request, queryset):
        """Bulk soft delete."""
        for obj in queryset:
            obj.soft_delete(user=request.user)
```

---

## URL Configuration

```python
"""URL configuration for {domain} API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from domain.{domain}.api.views import {Model}ViewSet

app_name = "{domain}"

router = DefaultRouter()
router.register(r"{models-kebab}", {Model}ViewSet, basename="{model-kebab}")

urlpatterns = [
    path("", include(router.urls)),
]
```

---

## __init__.py Exports

**models/__init__.py:**
```python
"""Domain models."""
from domain.{domain}.models.{model} import {Model}

__all__ = ["{Model}"]
```

**services/__init__.py:**
```python
"""Domain services."""
from .{model} import {Model}Service

__all__ = ["{Model}Service"]
```

**selectors/__init__.py:**
```python
"""Domain selectors."""
from .{model} import {Model}Selector

__all__ = ["{Model}Selector"]
```

**api/serializers/__init__.py:**
```python
"""Serializers for Domain API."""
from domain.{domain}.api.serializers.{model} import {Model}Serializer

__all__ = ["{Model}Serializer"]
```

**api/views/__init__.py:**
```python
"""Views for Domain API."""
from domain.{domain}.api.views.{model} import {Model}ViewSet

__all__ = ["{Model}ViewSet"]
```

---

## Implementation Checklist

### Core Implementation
- [ ] Create model file with all fields and Meta
- [ ] Create service with create/update/delete/restore
- [ ] Create selector with get_all/get_by_id/get_by_code/search/exists
- [ ] Create serializer with proper fields
- [ ] Create viewset with queryset method
- [ ] Register in admin.py
- [ ] Add URL route

### Exports & Integration
- [ ] Export model in models/__init__.py
- [ ] Export service in services/__init__.py
- [ ] Export selector in selectors/__init__.py
- [ ] Export serializer in api/serializers/__init__.py
- [ ] Export viewset in api/views/__init__.py

### Database
- [ ] Create migration: `python manage.py makemigrations {domain}`
- [ ] Apply migration: `python manage.py migrate`

### Testing
- [ ] Write model tests
- [ ] Write service tests
- [ ] Write selector tests
- [ ] Write API tests

---

## Key Principles

✓ **Use AuditModel** for all business entities  
✓ **Use keyword-only args** (`*,`) in services/selectors  
✓ **Use @staticmethod** for all service/selector methods  
✓ **Always soft delete** (check dependencies first!)  
✓ **Always track users** (created_by, updated_by, deleted_by)  
✓ **Validate before save** (call full_clean())  
✓ **Services modify**, **Selectors query**  
✓ **Keep API layer thin** (delegate to services/selectors)  

---

## Decision Guide (Quick)

- **Write / business rules:** `services/`
- **Read / query composition:** `selectors/`
- **HTTP validation + shape:** `api/serializers/`
- **Transactions / concurrency-sensitive workflows:** service methods with `transaction.atomic` (and `select_for_update` when needed)
- **Consistent API errors:** use shared exceptions in `domain/shared/exceptions.py`

(Full details in `DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md` → Section 16.)

## Common Patterns

### Status/Choice Constants
```python
# constants.py
class ModelStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
```

### Custom Validators
```python
# validators.py
def validate_code_format(value):
    if not re.match(r'^[A-Z0-9-]+$', value):
        raise ValidationError(_('Invalid code format'))
```

### Custom Manager
```python
class ModelManager(BaseManager):
    def get_current(self):
        return self.filter(is_current=True).first()
```

### Business Logic Methods
```python
# In model
def activate(self, user=None):
    self.status = Status.ACTIVE
    self.save_by(user=user)

# In service
@staticmethod
def activate(*, obj: Model, user=None) -> Model:
    obj.status = Status.ACTIVE
    obj.updated_by = user
    obj.save(update_fields=["status", "updated_at", "updated_by"])
    return obj
```

---

**For complete details, patterns, and examples, see the full [Implementation Guide](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)**
