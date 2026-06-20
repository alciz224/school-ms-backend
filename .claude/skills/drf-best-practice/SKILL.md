---
name: drf-best-practice
description: DRF patterns for this multi-portal Django app — ViewSets, @action, portal permissions, serializers, and common gotchas.
---

# DRF Best Practices for school-ms-backend

This project uses two view styles side-by-side. Pick the right one, then follow the patterns below.

## 1. View style decision

| Style | When | Found in |
|-------|------|----------|
| `ModelViewSet` + router | CRUD-heavy resources with custom sub-actions | academic, school_operations, enrollment, scheduling |
| `APIView` + explicit path | Stateless operations, single-purpose endpoints | account, assessment |

Mixins variant: use `GenericViewSet` (geography pattern) when you need CRUD but want to manually implement each action for fine-grained control. Use `ReadOnlyModelViewSet` for list+retrieve portals.

## 2. ModelViewSet pattern

```python
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MyModel.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return MyCreateSerializer
        elif self.action in ('update', 'partial_update'):
            return MyUpdateSerializer
        elif self.action == 'list':
            return MyListSerializer
        return MyDetailSerializer

    def get_queryset(self):
        qs = MyModel.objects.select_related('fk1', 'fk2')
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save()  # AuditModel handles user tracking in save()

    def perform_destroy(self, instance):
        # Soft delete — never call instance.delete() directly
        instance.soft_delete(user=self.request.user)
```

### @action methods

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class MyViewSet(viewsets.ModelViewSet):
    # List action (no pk in URL)
    @action(detail=False, methods=['get'])
    def current(self, request):
        obj = MySelector.get_current()
        if not obj:
            return Response({'detail': 'Not found'}, status=404)
        return Response(self.get_serializer(obj).data)

    # Detail action (pk in URL)
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        try:
            obj = MyService.activate(obj=obj, user=request.user)
            return Response(self.get_serializer(obj).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

    # Custom URL path (use url_path for kebab-case)
    @action(detail=True, methods=['post'], url_path='update-setting')
    def update_setting(self, request, pk=None):
        ...
```

Rules:
- `detail=True` → URL: `/{pk}/action-name/`
- `detail=False` → URL: `/action-name/`
- Default method is `GET`; always pass `methods=`
- Use `url_path='kebab-case'` when you need a specific URL segment
- The `get_serializer_class()` dispatch must include every `self.action` value used by @action methods
- Never call `.as_view()` on an @action method — the router handles this
- Return `Response(...)` directly, not `api_response()`, for consistency with this codebase's ViewSet pattern

## 3. APIView pattern

```python
class MyEndpointView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = MyInputSerializer  # for request validation

    def get(self, request, **kwargs):
        data = MySelector.get_stuff(...)
        serializer = MyOutputSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = MyService.do_stuff(**serializer.validated_data, user=request.user)
        return Response(MyOutputSerializer(result).data, status=201)
```

## 4. Multi-portal permissions

Five role values live in `request.session["current_role"]`: `SCHOOL_ADMIN`, `STAFF`, `TEACHER`, `STUDENT`, `PARENT`.

### Pre-built permission classes (from `domain.enrollment.api.permissions`)

| Class | Allows |
|-------|--------|
| `IsSchoolStaffOrAdmin` | `SCHOOL_ADMIN`, `STAFF` |
| `IsTeacher` | `TEACHER` |
| `IsStudent` | `STUDENT` |
| `IsParent` | `PARENT` |
| `HasPortalRole` | Any authenticated user with role in `view.required_roles` |

### Composition with `|` (OR)

```python
permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
```

This is the standard DRF `|` operator on `BasePermission` subclasses. It allows access if **any** permission in the chain passes.

### Filtering querysets by role in get_queryset()

```python
def get_queryset(self):
    qs = MyModel.objects.all()
    role = self.request.session.get('current_role')
    if role == 'TEACHER':
        qs = qs.filter(teacher__user=self.request.user)
    elif role == 'STUDENT':
        qs = qs.filter(student=self.request.user)
    return qs
```

Note: `self.action` is not available in the initial `get_queryset()` call — it gets set after. Use `get_queryset()` for role filtering, not action branching (use `get_serializer_class()` for that).

## 5. Serializer patterns

### Split by purpose (preferred in this codebase)

```python
# Request validation — plain Serializer, not ModelSerializer
class MyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=20, validators=[...])
    description = serializers.CharField(required=False, allow_blank=True)

# Response — ModelSerializer with read_only_fields
class MyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

# List — lightweight, annotated counts
class MyListSerializer(serializers.ModelSerializer):
    children_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = MyModel
        fields = ('id', 'name', 'code', 'children_count')
```

### Common gotchas

1. **Always call `is_valid(raise_exception=True)`** — never use `if serializer.is_valid():` without else; `raise_exception=True` produces proper DRF error responses.

2. **Type-aware field declarations** — explicitly declare field types on plain Serializers. DRF does **not** read Django model field validations automatically. A `CharField` in your model needs an explicit `serializers.CharField(max_length=...)` in the serializer.

3. **Decimal fields** — use `coerce_to_string=False` if you want numeric JSON values, or omit it for string values (and ensure the frontend types match):
   ```python
   amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
   ```

4. **Date fields** — always specify `input_formats` if the frontend sends non-ISO dates. Default is ISO 8601.

5. **PrimaryKeyRelatedField querysets** — ensure the queryset is not filtered by soft-delete when the frontend needs to reference soft-deleted records:
   ```python
   to_classroom = serializers.PrimaryKeyRelatedField(
       queryset=Classroom.objects.all_with_deleted()  # NOT .objects.all()
   )
   ```

6. **SerializerMethodField typing** — annotate with `@extend_schema_field` for OpenAPI correctness:
   ```python
   @extend_schema_field(serializers.IntegerField())
   def get_count(self, obj):
       return obj.some_count
   ```

7. **Unique validators on nested writes** — DRF auto-adds `UniqueTogetherValidator` from the model. When writing nested serializers, remove them with `validators = []` in `Meta` and validate uniqueness manually in `.validate()`.

8. **HiddenField for context** — inject request context without requiring client input:
   ```python
   owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
   ```

## 6. Selector / Service wiring

- **Views call Selectors for reads and Services for writes.** Never call models directly from views.
- Services use `@staticmethod` and keyword-only args (`*`):
  ```python
  class MyService:
      @staticmethod
      def activate(*, obj, user):
          ...
  ```
- Selectors return querysets or objects, never `Response` objects.

## 7. Common mistakes to avoid

| Mistake | Fix |
|---------|-----|
| Calling `instance.delete()` instead of soft delete | Call `instance.soft_delete(user=self.request.user)` |
| Using `ModelViewSet` without overriding `perform_destroy` | Always override to call soft_delete |
| Using `IsAuthenticated` on session-based (V2) views — `request.user` might be Anonymous | Check `request.user.is_authenticated` in permission or use session-based portal permissions |
| Importing models directly in views for complex queries | Use a Selector method |
| Forgetting to add new @action names to `get_serializer_class()` dispatch | Every value of `self.action` must be handled |
| Using `api_response()` in ViewSets (this project returns `Response()` from ViewSets) | `api_response()` is for account/auth views; ViewSets return `Response()` |
| Catching bare `Exception` in @action methods | Prefer specific domain exceptions (`ValidationException`, `NotFoundException`, etc.) — they get mapped to correct HTTP codes by the shared exception handler |
