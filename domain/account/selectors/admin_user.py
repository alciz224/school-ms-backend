"""
Admin user selectors.

Cross-domain profile building for the super-admin portal detail view.
"""

from itertools import chain

from domain.account.models import CustomUser
from domain.shared.exceptions import NotFoundException


class AdminUserSelector:
    """Selector for admin user management (super-admin portal)."""

    @staticmethod
    def get_all_users():
        """Return all active (non-deleted) users."""
        return CustomUser.objects.all().order_by("-date_joined")

    @staticmethod
    def get_user_by_id(*, user_id):
        """Return a user by ID or raise NotFoundException."""
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise NotFoundException(resource_type="User", resource_id=user_id)

    @staticmethod
    def get_user_profiles(*, user):
        """Build UserProfiles payload for the detail view.

        Aggregates data from school_operations, enrollment, and account domains.
        """
        school_list = AdminUserSelector._get_school_admin_schools(user)
        teacher_assignments = AdminUserSelector._get_teacher_assignments(user)
        student_enrollments = AdminUserSelector._get_student_enrollments(user)
        parent_children = AdminUserSelector._get_parent_children(user)

        return {
            "is_super_admin": user.is_staff,
            "school_admin_schools": school_list,
            "teacher_assignments": teacher_assignments,
            "student_enrollments": student_enrollments,
            "parent_children": parent_children,
        }

    @staticmethod
    def _get_school_admin_schools(user):
        """Return schools where user is director or registrar."""
        director_schools = user.directed_schools.filter(is_deleted=False).values("id", "name")
        registrar_schools = user.administered_schools.filter(is_deleted=False).values("id", "name")
        seen = set()
        result = []
        for s in chain(director_schools, registrar_schools):
            sid = str(s["id"])
            if sid not in seen:
                seen.add(sid)
                result.append({"id": sid, "name": s["name"]})
        return result

    @staticmethod
    def _get_teacher_assignments(user):
        """Return teacher assignment profile entries (via TeacherProfile)."""
        from domain.school_operations.models import SchoolYearTeacher

        qs = SchoolYearTeacher.objects.filter(
            teacher__user=user, is_deleted=False
        ).select_related(
            "school_year__school"
        ).only(
            "school_year_id", "school_year__name",
            "school_year__school_id", "school_year__school__name",
            "status",
        )
        return [
            {
                "school_year_id": str(a.school_year_id),
                "school_year_name": a.school_year.name,
                "school_id": str(a.school_year.school_id),
                "school_name": a.school_year.school.name,
                "status": a.status,
            }
            for a in qs
        ]

    @staticmethod
    def _get_student_enrollments(user):
        """Return student enrollment profile entries (via StudentProfile)."""
        from domain.enrollment.models import StudentEnrollment

        qs = StudentEnrollment.objects.filter(
            student__user=user, is_deleted=False
        ).select_related(
            "classroom__school_year_level__level",
            "classroom__school_year_level__school_year_cycle__school_year",
        )
        result = []
        for e in qs:
            syl = e.classroom.school_year_level if e.classroom else None
            syc = syl.school_year_cycle if syl else None
            school_year_obj = syc.school_year if syc else None
            level_obj = syl.level if syl else None
            result.append({
                "student_id": str(e.student_id),
                "student_name": f"{e.first_name} {e.last_name}".strip(),
                "school_year": str(school_year_obj.id) if school_year_obj else None,
                "level": level_obj.name if level_obj else None,
                "classroom": e.classroom.name if e.classroom else None,
                "status": e.enrollment_status,
            })
        return result

    @staticmethod
    def _get_parent_children(user):
        """Return parent-child profile entries (via ParentProfile)."""
        from domain.account.models import ParentChild

        qs = ParentChild.objects.filter(
            parent__user=user, is_deleted=False
        ).select_related("child")
        return [
            {
                "student_name": pc.child.full_name if pc.child else None,
                "school_year": None,
                "level": None,
                "classroom": None,
            }
            for pc in qs
        ]
