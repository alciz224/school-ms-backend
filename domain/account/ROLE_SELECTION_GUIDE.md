# Role Selection Feature - Implementation Guide

## Overview

The role selection feature allows authenticated users to switch between different roles (student, teacher, parent, admin, school_admin, super_admin) based on their relationships and permissions in the system.

## Architecture

### Key Components

1. **UserRole (Constants)** - `domain/account/constants.py`
   - Defines all available roles in the system
   - Session key constant for storing active role

2. **UserRoleSelector (Selector)** - `domain/account/selectors/user.py`
   - Determines available roles for a user based on relationships
   - Provides default role selection logic

3. **SelectRoleSerializer (Serializer)** - `domain/account/api/serializers/auth_v2.py`
   - Validates role selection requests
   - Ensures user has access to requested role

4. **SelectRoleView (View)** - `domain/account/api/views/auth_v2.py`
   - Handles POST requests to select a role
   - Stores selected role in Django session

5. **UserSerializer (Enhanced)** - `domain/account/api/serializers/user.py`
   - Returns `available_roles` - list of roles user can access
   - Returns `active_role` - currently selected role from session

## Role Detection Logic

### Role Assignment Rules

| Role | Detection Logic |
|------|----------------|
| **student** | User has `StudentEnrollment` records (non-deleted) |
| **teacher** | User has `SchoolYearTeacher` records (non-deleted) |
| **parent** | User has `ParentChild` relationships as parent (non-deleted) |
| **admin** | User has `is_staff=True` (not superuser) |
| **school_admin** | User has `is_staff=True` (not superuser) |
| **super_admin** | User has `is_superuser=True` |

### Default Role Priority

When a user logs in, a default role is automatically selected based on this priority:

1. **student** (highest priority)
2. **teacher**
3. **parent**
4. **admin**
5. **school_admin**
6. **super_admin** (lowest priority)

## API Endpoints

### POST /api/v2/auth/select-role/

Select the active role for the current session.

**Authentication:** Required (session-based)

**Request:**
```json
{
  "role": "student"
}
```

**Successful Response (200):**
```json
{
  "success": true,
  "message": "Role selected successfully.",
  "data": {
    "role": "student"
  }
}
```

**Error Responses:**

- **400 Bad Request** - Invalid role format
```json
{
  "success": false,
  "message": "Invalid request.",
  "error": {
    "code": "invalid_role",
    "details": {
      "role": ["Role must be one of: student, teacher, parent, admin, school_admin, super_admin"]
    }
  }
}
```

- **401 Unauthorized** - Not authenticated
```json
{
  "success": false,
  "message": "Authentication required."
}
```

- **403 Forbidden** - Role not allowed for user
```json
{
  "success": false,
  "message": "Invalid request.",
  "error": {
    "role": ["You do not have access to this role"]
  }
}
```

### Enhanced User Serializer

The `UserSerializer` now includes role information in all authenticated endpoints:

**Example: GET /api/v2/auth/status/**
```json
{
  "success": true,
  "message": "Session is active.",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "phone": "+224620123456",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "is_verified": true,
      "is_active": true,
      "security": {
        "score": 75,
        "level": "high"
      },
      "available_roles": ["student", "teacher"],
      "active_role": "student"
    },
    "authenticated": true
  }
}
```

## Usage Examples

### Frontend Integration

#### 1. Login and Check Available Roles

```javascript
// Login user
const loginResponse = await fetch('/api/v2/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    identifier: 'user@example.com',
    password: 'password123'
  }),
  credentials: 'include'
});

const loginData = await loginResponse.json();

// User data includes available_roles and active_role
console.log(loginData.data.user.available_roles); // ["student", "teacher"]
console.log(loginData.data.user.active_role);     // "student" (default)
```

#### 2. Switch Role

```javascript
// Switch to teacher role
const selectRoleResponse = await fetch('/api/v2/auth/select-role/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    role: 'teacher'
  }),
  credentials: 'include'
});

const roleData = await selectRoleResponse.json();
console.log(roleData.data.role); // "teacher"
```

#### 3. Check Current Role

```javascript
// Get current session status
const statusResponse = await fetch('/api/v2/auth/status/', {
  credentials: 'include'
});

const statusData = await statusResponse.json();
console.log(statusData.data.user.active_role); // Current active role
```

### Backend Usage

#### Get User's Available Roles

```python
from domain.account.selectors import UserRoleSelector

# Get all available roles for a user
available_roles = UserRoleSelector.get_available_roles(user)
# Returns: ['student', 'teacher']

# Get default role for a user
default_role = UserRoleSelector.get_default_role(user)
# Returns: 'student' (highest priority available)
```

#### Access Active Role in Views

```python
from domain.account.constants import ACTIVE_ROLE_SESSION_KEY

def my_view(request):
    # Get active role from session
    active_role = request.session.get(ACTIVE_ROLE_SESSION_KEY)
    
    if active_role == UserRole.TEACHER:
        # Handle teacher-specific logic
        pass
    elif active_role == UserRole.STUDENT:
        # Handle student-specific logic
        pass
```

## Session Storage

- **Session Key:** `"active_role"`
- **Storage:** Django session (server-side)
- **Lifetime:** Tied to session lifetime (configurable in Django settings)
- **Persistence:** Persists across requests until session expires or user logs out

## Testing

Comprehensive test suite available at `domain/account/tests/test_api_role_selection.py`

**Run tests:**
```bash
pytest domain/account/tests/test_api_role_selection.py -v
```

**Test Coverage:**
- ✅ Role selection with authentication
- ✅ Validation of available roles
- ✅ Session persistence
- ✅ Role switching
- ✅ Default role assignment on login
- ✅ Role detection for all role types
- ✅ Soft-deleted relationships handling

## Security Considerations

1. **Authentication Required:** All role operations require an authenticated session
2. **Role Validation:** Users can only select roles they have access to
3. **Session-Based:** Role is stored server-side in Django session, not client-side
4. **CSRF Protection:** All POST requests require CSRF token
5. **Audit Trail:** Consider adding logging for role switches (future enhancement)

## Common Use Cases

### 1. Multi-Role User Portal

A user who is both a teacher and a parent can switch between viewing:
- Their teaching schedule and student grades (teacher role)
- Their children's performance and attendance (parent role)

### 2. Admin Dashboard

Staff members can switch between:
- Regular admin tasks (admin role)
- School-specific administration (school_admin role)

### 3. Student-Teacher Accounts

A teaching assistant who is also enrolled as a graduate student can switch between:
- Accessing their own courses (student role)
- Managing classes they assist with (teacher role)

## Troubleshooting

### Issue: Role not appearing in available_roles

**Cause:** User doesn't have the required relationship
**Solution:** Verify the user has:
- StudentEnrollment (for student role)
- SchoolYearTeacher (for teacher role)
- ParentChild relationship (for parent role)
- Appropriate flags (is_staff/is_superuser for admin roles)

### Issue: Role selection returns 403

**Cause:** User trying to select a role they don't have access to
**Solution:** Check `available_roles` before attempting to select a role

### Issue: active_role is null after login

**Cause:** User has no available roles
**Solution:** This is expected behavior. Assign appropriate relationships to the user.

## Future Enhancements

1. **Role-Based Permissions:** Integrate with DRF permissions for automatic endpoint access control
2. **Audit Logging:** Track role switches for security monitoring
3. **Role-Specific Dashboards:** Auto-redirect based on active role
4. **Time-Based Role Restrictions:** Limit role access based on time periods
5. **Role Hierarchy:** Implement role inheritance and permission cascading

## Related Documentation

- [API Contract](auth/tables/select_role.yaml) - OpenAPI specification
- [User Model](domain/account/models/user.py) - User authentication model
- [Authentication Flow](auth/v2/API_CONTRACT.md) - Session-based auth documentation

## Support

For issues or questions:
1. Check existing tests for usage examples
2. Review the OpenAPI specification
3. Consult the implementation in `domain/account/`

---

**Last Updated:** 2024-02-19  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
