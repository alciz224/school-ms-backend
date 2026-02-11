"""Portal-oriented roster views (classroom lists, student enrollments, etc.)."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from domain.enrollment.api.permissions import (
    HasPortalRole,
    IsParent,
    IsSchoolStaffOrAdmin,
    IsStudent,
    IsTeacher,
)
from domain.enrollment.api.serializers import (
    ClassroomRosterSerializer,
    StudentEnrollmentRosterSerializer,
)
from domain.enrollment.selectors import RosterSelector
from domain.shared.exceptions import NotFoundException


class ClassroomRosterViewSet(ReadOnlyModelViewSet):
    """
    Roster views for classrooms.
    
    Permissions:
    - SCHOOL_ADMIN / STAFF: full access
    - TEACHER: access to own classrooms (TODO: filter by teacher assignment)
    """

    permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
    serializer_class = ClassroomRosterSerializer

    def get_queryset(self):
        # For now, return all. Later: filter by teacher assignment if TEACHER role.
        from domain.enrollment.models import Classroom

        return Classroom.objects.all()

    @action(detail=True, methods=["get"], url_path="students")
    def students(self, request, pk=None):
        """Get the roster (list of students) for a specific classroom."""
        classroom = self.get_object()
        enrollments = RosterSelector.get_classroom_roster(classroom_id=classroom.id)
        serializer = StudentEnrollmentRosterSerializer(enrollments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        """Get classroom with stats (student count, capacity remaining)."""
        classroom = RosterSelector.get_classroom_with_stats(classroom_id=int(pk))
        if not classroom:
            raise NotFoundException(resource_type="Classroom", resource_id=pk)
        serializer = ClassroomRosterSerializer(classroom)
        return Response(serializer.data)


class SchoolYearLevelEnrollmentsView(APIView):
    """
    Get all enrollments for a school year level.
    
    Permissions: SCHOOL_ADMIN / STAFF
    """

    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, school_year_level_id):
        enrollments = RosterSelector.get_school_year_level_enrollments(
            school_year_level_id=school_year_level_id
        )
        serializer = StudentEnrollmentRosterSerializer(enrollments, many=True)
        return Response(serializer.data)


class MyEnrollmentsView(APIView):
    """
    Student portal: get my own enrollments.
    
    Permissions: STUDENT role
    """

    permission_classes = [IsStudent]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        enrollments = RosterSelector.get_student_enrollments(student_id=request.user.id)
        serializer = StudentEnrollmentRosterSerializer(enrollments, many=True)
        return Response(serializer.data)


class MyChildrenEnrollmentsView(APIView):
    """
    Parent portal: get enrollments for my children.
    
    Permissions: PARENT role
    
    TODO: Implement parent-child relationship model/selector.
    For now, returns empty list as placeholder.
    """

    permission_classes = [IsParent]

    def get(self, request):
        # TODO: implement parent-child link and fetch children's enrollments
        # children_ids = ParentChildSelector.get_children_ids(parent_id=request.user.id)
        # enrollments = StudentEnrollment.objects.filter(student_id__in=children_ids, is_deleted=False)
        return Response([])


class MyClassesView(APIView):
    """
    Teacher portal: get classrooms assigned to me.
    
    Permissions: TEACHER role
    """

    permission_classes = [IsTeacher]

    def get(self, request):
        from domain.enrollment.selectors import TeacherAssignmentSelector
        
        assignments = TeacherAssignmentSelector.get_teacher_classes(teacher_user_id=request.user.id)
        
        # Group by classroom and return classroom info with subjects
        classrooms_data = {}
        for assignment in assignments:
            classroom_id = assignment.classroom.id
            if classroom_id not in classrooms_data:
                classrooms_data[classroom_id] = {
                    "id": assignment.classroom.id,
                    "name": assignment.classroom.name,
                    "school_year_level": {
                        "id": assignment.school_year_level.id,
                        "level_name": assignment.school_year_level.level.name,
                        "cycle_name": assignment.school_year_level.school_year_cycle.cycle.name,
                    },
                    "subjects": []
                }
            
            classrooms_data[classroom_id]["subjects"].append({
                "id": assignment.school_year_level_subject.id,
                "subject_name": assignment.subject.name,
                "coefficient": str(assignment.school_year_level_subject.coefficient),
                "assignment_id": assignment.id,
            })
        
        return Response(list(classrooms_data.values()))
