from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.finance.api.views.fee_type import FeeTypeViewSet
from domain.finance.api.views.school_fee import SchoolFeeViewSet
from domain.finance.api.views.student_payment import StudentPaymentViewSet

app_name = "finance"

router = DefaultRouter()
router.register(r"fee-types", FeeTypeViewSet, basename="fee-type")
router.register(r"school-fees", SchoolFeeViewSet, basename="school-fee")
router.register(r"student-payments", StudentPaymentViewSet, basename="student-payment")

urlpatterns = [
    path("", include(router.urls)),
]
