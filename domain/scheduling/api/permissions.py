"""Permissions for scheduling API.

Reuses permissions from enrollment domain.
"""

from domain.enrollment.api.permissions import (
    IsSchoolStaffOrAdmin,
    IsTeacher,
    IsStudent,
    IsParent,
)

__all__ = [
    "IsSchoolStaffOrAdmin",
    "IsTeacher",
    "IsStudent",
    "IsParent",
]
