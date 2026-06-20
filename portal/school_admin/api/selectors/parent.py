from django.db.models import Q, Prefetch

from domain.account.models import CustomUser, ParentChild
from domain.enrollment.models import StudentEnrollment


class SchoolAdminParentSelector:
    """
    Sélecteurs pour la liste des parents côté portail school admin.

    Depuis la refonte des profils, la chaîne d'accès est :
        CustomUser → parent_profile → children_relationships (ParentChild)
        → child (StudentProfile) → user (CustomUser) / student_enrollments
    """

    @staticmethod
    def list(*, search: str = None, has_email: bool = None, has_phone: bool = None) -> list:
        # Prefetch des inscriptions actives par StudentProfile
        enrollment_qs = (
            StudentEnrollment.objects.filter(is_deleted=False)
            .select_related(
                "classroom",
                "school_year_level__level",
                "school_year_level__school_year_cycle__school_year",
            )
            .order_by("-enrollment_date")
        )

        # Prefetch des ParentChild via parent_profile
        pc_prefetch = Prefetch(
            "parent_profile__children_relationships",
            queryset=(
                ParentChild.objects.filter(is_deleted=False)
                .select_related("child__user")
                .prefetch_related(
                    Prefetch(
                        "child__student_enrollments",
                        queryset=enrollment_qs,
                        to_attr="latest_enrollments",
                    )
                )
            ),
            to_attr="active_children_rels",
        )

        qs = (
            CustomUser.objects.filter(
                is_active=True,
                parent_profile__isnull=False,
                parent_profile__children_relationships__is_deleted=False,
            )
            .select_related("parent_profile")
            .prefetch_related(pc_prefetch)
            .distinct()
        )

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )

        if has_email is True:
            qs = qs.filter(email__isnull=False).exclude(email="")
        elif has_email is False:
            qs = qs.filter(Q(email__isnull=True) | Q(email=""))

        if has_phone is True:
            qs = qs.filter(phone__isnull=False).exclude(phone="")
        elif has_phone is False:
            qs = qs.filter(Q(phone__isnull=True) | Q(phone=""))

        qs = qs.order_by("first_name", "last_name")

        # Aplatissement pour matcher la forme attendue par le frontend
        parents_list = []
        for parent_user in qs:
            children_data = []
            relationships = getattr(parent_user.parent_profile, "active_children_rels", [])
            for pc in relationships:
                child_profile = pc.child
                child_user = child_profile.user  # toujours présent (refonte profil)
                enrollments = getattr(child_profile, "latest_enrollments", [])

                if enrollments:
                    enrollment = enrollments[0]
                    syl = enrollment.school_year_level
                    children_data.append({
                        "id": str(child_user.id),
                        "full_name": child_profile.full_name,
                        "class_name": enrollment.classroom.name if enrollment.classroom else "",
                        "level": syl.level.name if syl and syl.level else "",
                        "academic_year": (
                            syl.school_year_cycle.school_year.name
                            if syl and syl.school_year_cycle and syl.school_year_cycle.school_year
                            else ""
                        ),
                        "enrollment_status": enrollment.enrollment_status,
                    })
                else:
                    children_data.append({
                        "id": str(child_user.id),
                        "full_name": child_profile.full_name,
                        "class_name": "",
                        "level": "",
                        "academic_year": "",
                        "enrollment_status": "",
                    })

            parent_user.children = children_data
            parent_user.children_count = len(children_data)
            parents_list.append(parent_user)

        return parents_list
