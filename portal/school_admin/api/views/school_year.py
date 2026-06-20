from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.school_operations.models import (
    SchoolYear, SchoolYearCycle, SchoolYearLevel,
    SchoolYearLevelSubject, SchoolYearCycleTimeSlot,
)
from domain.enrollment.models import Classroom

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from rest_framework import serializers


class SchoolYearSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_id = serializers.CharField()
    name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.CharField()


class SchoolYearCycleSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_year_id = serializers.CharField()
    cycle_id = serializers.CharField()
    term_type_id = serializers.CharField()


class SchoolYearLevelSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_year_cycle_id = serializers.CharField()
    level_id = serializers.CharField()
    track_id = serializers.CharField(allow_null=True, default=None)


class SchoolYearLevelSubjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_year_level_id = serializers.CharField()
    subject_id = serializers.CharField()
    coefficient = serializers.IntegerField()


class ClassroomSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_year_level_id = serializers.CharField()
    name = serializers.CharField()
    capacity = serializers.IntegerField(allow_null=True, default=None)
    room_number = serializers.CharField(allow_null=True, default=None)


class TimeSlotSerializer(serializers.Serializer):
    id = serializers.CharField()
    school_year_cycle_id = serializers.CharField()
    name = serializers.CharField()
    order = serializers.IntegerField()
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")
    duration_minutes = serializers.IntegerField()
    status = serializers.CharField()


class SchoolYearBySchoolView(APIView):
    """
    List school years for a school.
    GET /schools/{schoolId}/school-years/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("schoolId", OpenApiTypes.STR, OpenApiParameter.PATH),
        ],
        responses=SchoolYearSerializer(many=True),
    )
    def get(self, request, school_id=None):
        qs = SchoolYear.objects.filter(
            school_id=school_id, is_deleted=False
        ).select_related("school")
        serializer = SchoolYearSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SchoolYearDetailView(APIView):
    """
    Get a school year by ID.
    GET /schools/school-years/{id}/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearSerializer)
    def get(self, request, id=None):
        try:
            sy = SchoolYear.objects.get(id=id, is_deleted=False)
        except SchoolYear.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "School year not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SchoolYearSerializer(sy)
        return Response({"success": True, "data": serializer.data})


class SchoolYearCyclesView(APIView):
    """
    List cycles for a school year.
    GET /schools/school-years/{schoolYearId}/cycles/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearCycleSerializer(many=True))
    def get(self, request, school_year_id=None):
        qs = SchoolYearCycle.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        )
        serializer = SchoolYearCycleSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SchoolYearCycleLevelsView(APIView):
    """
    List levels for a school year cycle.
    GET /schools/school-year-cycles/{schoolYearCycleId}/levels/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearLevelSerializer(many=True))
    def get(self, request, school_year_cycle_id=None):
        qs = SchoolYearLevel.objects.filter(
            school_year_cycle_id=school_year_cycle_id, is_deleted=False
        ).select_related("level", "track")
        serializer = SchoolYearLevelSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SchoolYearLevelSubjectsView(APIView):
    """
    List subjects for a school year level.
    GET /schools/school-year-levels/{schoolYearLevelId}/subjects/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearLevelSubjectSerializer(many=True))
    def get(self, request, school_year_level_id=None):
        qs = SchoolYearLevelSubject.objects.filter(
            school_year_level_id=school_year_level_id, is_deleted=False
        ).select_related("subject")
        serializer = SchoolYearLevelSubjectSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SchoolYearLevelClassroomsView(APIView):
    """
    List classrooms for a school year level.
    GET /schools/school-year-levels/{schoolYearLevelId}/classrooms/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=ClassroomSerializer(many=True))
    def get(self, request, school_year_level_id=None):
        qs = Classroom.objects.filter(
            school_year_level_id=school_year_level_id, is_deleted=False
        )
        serializer = ClassroomSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SchoolYearCycleTimeSlotsView(APIView):
    """
    List time slots for a school year cycle.
    GET /schools/school-year-cycles/{schoolYearCycleId}/time-slots/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=TimeSlotSerializer(many=True))
    def get(self, request, school_year_cycle_id=None):
        qs = SchoolYearCycleTimeSlot.objects.filter(
            school_year_cycle_id=school_year_cycle_id, is_deleted=False
        ).order_by("order")
        serializer = TimeSlotSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


# --- Bulk Configuration ---

class SubjectConfigSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    coefficient = serializers.IntegerField(min_value=1, max_value=10)


class ClassroomConfigSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    capacity = serializers.IntegerField(required=False, allow_null=True)
    room_number = serializers.CharField(required=False, allow_null=True, max_length=50)


class LevelConfigSerializer(serializers.Serializer):
    level_id = serializers.IntegerField()
    track_id = serializers.IntegerField(required=False, allow_null=True)
    subjects = SubjectConfigSerializer(many=True, required=False, default=list)
    classrooms = ClassroomConfigSerializer(many=True, required=False, default=list)


class CycleConfigSerializer(serializers.Serializer):
    cycle_id = serializers.IntegerField()
    term_type_id = serializers.IntegerField()
    levels = LevelConfigSerializer(many=True, required=False, default=list)


class TimeSlotConfigSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    order = serializers.IntegerField()


class CycleTimeSlotsSerializer(serializers.Serializer):
    cycle_id = serializers.IntegerField()
    slots = TimeSlotConfigSerializer(many=True)


class BulkSchoolYearConfigSerializer(serializers.Serializer):
    school_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    cycles = CycleConfigSerializer(many=True, required=False, default=list)
    time_slots = CycleTimeSlotsSerializer(many=True, required=False, default=list)


class SchoolYearConfigureView(APIView):
    """
    Crée une année scolaire avec sa configuration complète en une seule requête atomique.

    POST /schools/configure/
    Accepte la charge utile complète du wizard et orchestre la création de :
        - AcademicYear (référentiel global, récupéré ou créé)
        - SchoolYear
        - SchoolYearCycle (par cycle)
        - SchoolYearLevel (par niveau)
        - SchoolYearLevelSubject (par matière/coefficient)
        - Classroom (par classe)
        - SchoolYearCycleTimeSlot (par créneau)

    En cas d'erreur sur un sous-objet, la transaction est annulée intégralement.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        request=BulkSchoolYearConfigSerializer,
        responses=SchoolYearSerializer,
    )
    def post(self, request):
        from django.core.exceptions import ValidationError as DjangoValidationError

        from domain.school_operations.services.school_year import SchoolYearService
        from domain.school_operations.services.school_year_cycle import SchoolYearCycleService
        from domain.school_operations.services.school_year_level import SchoolYearLevelService

        from domain.academic.models import AcademicYear
        from domain.school_operations.models import School

        # ----- Validation du payload -----
        serializer = BulkSchoolYearConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user

        # ----- Validations métier en amont (avant ouverture de transaction) -----
        try:
            school = School.objects.get(id=data["school_id"], is_deleted=False)
        except School.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "school_not_found",
                        "message": "École introuvable.",
                        "details": {"school_id": data["school_id"]},
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Dérive le code de l'année académique depuis les dates (Sept N -> Juin N+1)
        start_year_int = data["start_date"].year
        end_year_int = data["end_date"].year
        if end_year_int != start_year_int + 1:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "invalid_academic_period",
                        "message": "L'année académique doit couvrir deux années calendaires consécutives (ex : Sept 2025 -> Juin 2026).",
                        "details": {
                            "start_date": str(data["start_date"]),
                            "end_date": str(data["end_date"]),
                        },
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        academic_year_code = f"{start_year_int}-{end_year_int}"

        # ----- Récupère ou crée l'AcademicYear (référentiel global) -----
        academic_year = AcademicYear.objects.filter(code=academic_year_code).first()
        if academic_year is None:
            try:
                academic_year = AcademicYear.objects.create(
                    code=academic_year_code,
                    start_year=start_year_int,
                    end_year=end_year_int,
                )
            except DjangoValidationError as exc:
                return Response(
                    {
                        "success": False,
                        "error": {
                            "code": "invalid_academic_year",
                            "message": "Impossible de créer l'année académique.",
                            "details": exc.message_dict if hasattr(exc, "message_dict") else {"errors": exc.messages},
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ----- Vérifie que cette école n'a pas déjà une SchoolYear pour cette année académique -----
        existing = SchoolYear.objects.filter(
            school=school,
            academic_year=academic_year,
            is_deleted=False,
        ).first()
        if existing is not None:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "school_year_already_exists",
                        "message": f"L'année scolaire {academic_year_code} existe déjà pour cette école.",
                        "details": {
                            "school_year_id": str(existing.id),
                            "academic_year_code": academic_year_code,
                        },
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )

        # ----- Création atomique de toute la configuration -----
        try:
            with transaction.atomic():
                school_year = SchoolYearService.create_school_year(
                    school=school,
                    academic_year=academic_year,
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    user=user,
                )

                cycle_map = {}
                created_levels = 0
                created_subjects = 0
                created_classrooms = 0

                for cycle_config in data.get("cycles", []):
                    cycle = SchoolYearCycleService.create(
                        school_year_id=school_year.id,
                        cycle_id=cycle_config["cycle_id"],
                        term_type_id=cycle_config["term_type_id"],
                        created_by=user if user.is_authenticated else None,
                    )
                    cycle_map[cycle_config["cycle_id"]] = cycle

                    for level_config in cycle_config.get("levels", []):
                        level = SchoolYearLevelService.create(
                            school_year_cycle_id=cycle.id,
                            level_id=level_config["level_id"],
                            track_id=level_config.get("track_id"),
                            created_by=user if user.is_authenticated else None,
                        )
                        created_levels += 1

                        for subject_config in level_config.get("subjects", []):
                            SchoolYearLevelSubject.objects.create(
                                school_year_level=level,
                                subject_id=subject_config["subject_id"],
                                coefficient=subject_config["coefficient"],
                                created_by=user if user.is_authenticated else None,
                                updated_by=user if user.is_authenticated else None,
                            )
                            created_subjects += 1

                        for classroom_config in level_config.get("classrooms", []):
                            Classroom.objects.create(
                                school_year_level=level,
                                name=classroom_config["name"],
                                capacity=classroom_config.get("capacity"),
                                room_number=classroom_config.get("room_number"),
                                created_by=user if user.is_authenticated else None,
                                updated_by=user if user.is_authenticated else None,
                            )
                            created_classrooms += 1

                created_time_slots = 0
                for ts_config in data.get("time_slots", []):
                    cycle = cycle_map.get(ts_config["cycle_id"])
                    if cycle is None:
                        raise DjangoValidationError({
                            "time_slots": f"Le cycle {ts_config['cycle_id']} n'a pas été créé dans cette requête."
                        })
                    for slot in ts_config["slots"]:
                        SchoolYearCycleTimeSlot.objects.create(
                            school_year_cycle=cycle,
                            name=slot["name"],
                            start_time=slot["start_time"],
                            end_time=slot["end_time"],
                            order=slot["order"],
                            created_by=user if user.is_authenticated else None,
                            updated_by=user if user.is_authenticated else None,
                        )
                        created_time_slots += 1

        except DjangoValidationError as exc:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "configuration_validation_failed",
                        "message": "La configuration soumise contient des erreurs de validation.",
                        "details": exc.message_dict if hasattr(exc, "message_dict") else {"errors": exc.messages},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----- Réponse de succès enrichie -----
        return Response(
            {
                "success": True,
                "data": {
                    **SchoolYearSerializer(school_year).data,
                    "academic_year_code": academic_year_code,
                    "summary": {
                        "cycles_created": len(cycle_map),
                        "levels_created": created_levels,
                        "subjects_created": created_subjects,
                        "classrooms_created": created_classrooms,
                        "time_slots_created": created_time_slots,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


class SchoolYearReconfigureView(APIView):
    """
    Met à jour la configuration complète d'une année scolaire existante (édition wizard).

    PUT /schools/school-years/{id}/configure/
    Accepte la même charge utile que la création et réconcilie l'état désiré avec
    l'existant, de façon atomique :
        - SchoolYear : nom et dates mis à jour
        - Cycles / niveaux / matières / salles : créés, mis à jour ou retirés
        - Tout élément retiré est supprimé via le service correspondant, dont les
          gardes métier (`can_delete`) bloquent la suppression d'une donnée déjà
          utilisée (inscriptions, notes...) avec un message en français.

    En cas d'erreur (validation ou règle métier), la transaction est annulée
    intégralement et rien n'est modifié.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        request=BulkSchoolYearConfigSerializer,
        responses=SchoolYearSerializer,
    )
    def put(self, request, id=None):
        from domain.school_operations.services.school_year_cycle import SchoolYearCycleService
        from domain.school_operations.services.school_year_level import SchoolYearLevelService
        from domain.shared.exceptions import BusinessRuleException

        serializer = BulkSchoolYearConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user
        actor = user if user.is_authenticated else None

        try:
            school_year = SchoolYear.objects.get(id=id, is_deleted=False)
        except SchoolYear.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "school_year_not_found",
                        "message": "Année scolaire introuvable.",
                        "details": {"id": str(id)},
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        summary = {
            "cycles_created": 0, "cycles_updated": 0, "cycles_deleted": 0,
            "levels_created": 0, "levels_updated": 0, "levels_deleted": 0,
            "subjects_created": 0, "subjects_updated": 0, "subjects_deleted": 0,
            "classrooms_created": 0, "classrooms_updated": 0, "classrooms_deleted": 0,
        }

        with transaction.atomic():
            # --- 1. Mise à jour des champs de l'année scolaire ---
            school_year.name = data["name"]
            school_year.start_date = data["start_date"]
            school_year.end_date = data["end_date"]
            school_year.save_by(user=actor)

            desired_cycles = {c["cycle_id"]: c for c in data.get("cycles", [])}

            # --- 2. Upsert (création / mise à jour) de l'état désiré ---
            for cycle_id, cycle_config in desired_cycles.items():
                cyc = school_year.cycles.filter(
                    cycle_id=cycle_id, is_deleted=False
                ).first()
                if cyc is None:
                    cyc = SchoolYearCycleService.create(
                        school_year_id=school_year.id,
                        cycle_id=cycle_id,
                        term_type_id=cycle_config["term_type_id"],
                        created_by=actor,
                    )
                    summary["cycles_created"] += 1
                elif cyc.term_type_id != cycle_config["term_type_id"]:
                    SchoolYearCycleService.update(
                        school_year_cycle=cyc,
                        term_type_id=cycle_config["term_type_id"],
                        updated_by=actor,
                    )
                    summary["cycles_updated"] += 1

                for level_config in cycle_config.get("levels", []):
                    track_id = level_config.get("track_id")
                    lvl = cyc.levels.filter(
                        level_id=level_config["level_id"],
                        track_id=track_id,
                        is_deleted=False,
                    ).first()
                    if lvl is None:
                        lvl = SchoolYearLevelService.create(
                            school_year_cycle_id=cyc.id,
                            level_id=level_config["level_id"],
                            track_id=track_id,
                            created_by=actor,
                        )
                        summary["levels_created"] += 1

                    # Matières du niveau
                    for subj in level_config.get("subjects", []):
                        ex = lvl.level_subjects.filter(
                            subject_id=subj["subject_id"], is_deleted=False
                        ).first()
                        if ex is None:
                            SchoolYearLevelSubject.objects.create(
                                school_year_level=lvl,
                                subject_id=subj["subject_id"],
                                coefficient=subj["coefficient"],
                                created_by=actor,
                                updated_by=actor,
                            )
                            summary["subjects_created"] += 1
                        elif ex.coefficient != subj["coefficient"]:
                            ex.coefficient = subj["coefficient"]
                            ex.updated_by = actor
                            ex.save()
                            summary["subjects_updated"] += 1

                    # Salles du niveau (identifiées par nom)
                    for cr in level_config.get("classrooms", []):
                        ex = lvl.classrooms.filter(
                            name=cr["name"], is_deleted=False
                        ).first()
                        if ex is None:
                            Classroom.objects.create(
                                school_year_level=lvl,
                                name=cr["name"],
                                capacity=cr.get("capacity"),
                                room_number=cr.get("room_number"),
                                created_by=actor,
                                updated_by=actor,
                            )
                            summary["classrooms_created"] += 1
                        elif (
                            ex.capacity != cr.get("capacity")
                            or ex.room_number != cr.get("room_number")
                        ):
                            ex.capacity = cr.get("capacity")
                            ex.room_number = cr.get("room_number")
                            ex.updated_by = actor
                            ex.save()
                            summary["classrooms_updated"] += 1

            # --- 3. Suppressions, des feuilles vers la racine (gardes métier) ---
            def _delete_classroom(classroom):
                if not classroom.can_delete():
                    raise BusinessRuleException(
                        message=f"La classe « {classroom.name} » a des élèves inscrits et ne peut pas être retirée.",
                        code="classroom_in_use",
                        rule="classroom_can_delete",
                    )
                classroom.soft_delete(user=actor)
                summary["classrooms_deleted"] += 1

            def _delete_subject(subject):
                if not subject.can_delete():
                    raise BusinessRuleException(
                        message="Cette matière est utilisée par des évaluations ou des notes et ne peut pas être retirée.",
                        code="subject_in_use",
                        rule="school_year_level_subject_can_delete",
                    )
                subject.soft_delete(user=actor)
                summary["subjects_deleted"] += 1

            def _delete_level_subtree(level):
                for classroom in level.classrooms.filter(is_deleted=False):
                    _delete_classroom(classroom)
                for subject in level.level_subjects.filter(is_deleted=False):
                    _delete_subject(subject)
                SchoolYearLevelService.delete(school_year_level=level, deleted_by=actor)
                summary["levels_deleted"] += 1

            def _delete_cycle_subtree(cycle):
                for level in cycle.levels.filter(is_deleted=False):
                    _delete_level_subtree(level)
                SchoolYearCycleService.delete(school_year_cycle=cycle, deleted_by=actor)
                summary["cycles_deleted"] += 1

            for cyc in school_year.cycles.filter(is_deleted=False):
                cycle_config = desired_cycles.get(cyc.cycle_id)
                if cycle_config is None:
                    _delete_cycle_subtree(cyc)
                    continue

                desired_levels = {
                    (lc["level_id"], lc.get("track_id")): lc
                    for lc in cycle_config.get("levels", [])
                }
                for lvl in cyc.levels.filter(is_deleted=False):
                    level_config = desired_levels.get((lvl.level_id, lvl.track_id))
                    if level_config is None:
                        _delete_level_subtree(lvl)
                        continue

                    desired_subject_ids = {
                        s["subject_id"] for s in level_config.get("subjects", [])
                    }
                    for subject in lvl.level_subjects.filter(is_deleted=False):
                        if subject.subject_id not in desired_subject_ids:
                            _delete_subject(subject)

                    desired_names = {
                        c["name"] for c in level_config.get("classrooms", [])
                    }
                    for classroom in lvl.classrooms.filter(is_deleted=False):
                        if classroom.name not in desired_names:
                            _delete_classroom(classroom)

        school_year.refresh_from_db()
        return Response(
            {
                "success": True,
                "data": {
                    **SchoolYearSerializer(school_year).data,
                    "summary": summary,
                },
            },
            status=status.HTTP_200_OK,
        )
