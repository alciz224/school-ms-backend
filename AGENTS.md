# school-ms-backend — OpenCode guide

## Project

Django 6.0 school management system following DDD. Frontend (TanStack Start) is a separate project at `C:\Users\Daniela\Desktop\School Management System\frontent\my-tanstack-app\my-tanstack-app`.

## Commands

```powershell
uv run python manage.py <command>     # Django management
uv run pytest                          # all tests
uv run pytest path/to/test_file.py    # single test file
uv run pytest -k test_name            # single test by name
uv run python manage.py spectacular --file schema.yml  # regenerate OpenAPI schema
```

## Architecture

- **Domain apps** under `domain/` follow strict DDD layout:
  ```
  domain/{app}/
    models/{model}.py          # one file per model, all inherit AuditModel
    services/{model}.py        # write logic, @staticmethod, keyword-only args
    selectors/{model}.py       # read logic, @staticmethod, keyword-only args
    api/serializers/{model}.py
    api/views/{model}.py
    api/urls.py
    tests/
  ```
- **Portal apps** under `portal/` (school_admin, system_admin, teacher, student, parent).
- **Config** in `config/` (settings, urls with API v1 JWT + API v2 session-based routing).

## Key conventions

- **Soft delete** by default; call `.hard_delete()` only when explicit.
- **CustomUser** in `domain.account` — login via email or phone.
- Consistent API responses: `{"success": bool, "message": str|null, "data": ...}`.
- Domain exceptions (`ValidationException`, `NotFoundException`, `ConflictException`, `PermissionDeniedException`, `BusinessRuleException`) mapped to HTTP via custom DRF handler.
- Two auth systems: JWT (V1, 30-min access + 7-day refresh with rotation) and session-based (V2, CSRF-protected).
- No .env files; settings live directly in `config/settings.py` (dev secret key exposed).
- Dev admin: `admin@school-ms.com` / `Admin@123`.

## Testing quirks

- `DJANGO_SETTINGS_MODULE=config.settings` (set in pyproject.toml).
- Dirs excluded from test discovery: `ref`, `tables`, `auth/tables`, `tmp_rovodev_*`.
- conftest.py in each domain app under `tests/`.

## Linting / formatting

No linter or formatter config exists in this repo. Do not add one without asking.

## API contracts

Frontend TypeScript types are the **source of truth** for API payloads. Before changing a serializer, read the corresponding `src/server/data/{domain}/types.ts` from the frontend repo. See `.agent/skills/frontend-contract-sync/SKILL.md`.

## Schema

drf-spectacular serves OpenAPI at `/api/schema/`, Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`. Regenerate with `uv run python manage.py spectacular --file schema.yml`.
