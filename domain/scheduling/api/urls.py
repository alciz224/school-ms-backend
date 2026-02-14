"""URL configuration for scheduling API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.scheduling.api.views import (
    ScheduleViewSet,
    ScheduleConflictCheckView,
    ClassroomTimetableView,
    TeacherScheduleView,
    StudentTimetableView,
    BulkScheduleCreateView,
)

app_name = 'scheduling'

router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('schedules/check-conflicts/', ScheduleConflictCheckView.as_view(), name='schedule-check-conflicts'),
    path('schedules/bulk-create/', BulkScheduleCreateView.as_view(), name='schedule-bulk-create'),
    path('timetables/classroom/<int:classroom_id>/', ClassroomTimetableView.as_view(), name='timetable-classroom'),
    path('timetables/teacher/<int:teacher_id>/', TeacherScheduleView.as_view(), name='timetable-teacher'),
    path('timetables/student/<int:student_id>/', StudentTimetableView.as_view(), name='timetable-student'),
]
