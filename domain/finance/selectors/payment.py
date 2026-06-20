from django.db.models import Prefetch

from domain.finance.models import SchoolFee, StudentPayment


class PaymentSelector:
    @staticmethod
    def list_by_enrollment(student_enrollment_id: int):
        return StudentPayment.objects.filter(
            student_enrollment_id=student_enrollment_id, is_deleted=False
        ).select_related("school_fee__fee_type").order_by("-payment_date")

    @staticmethod
    def list_by_classroom(classroom_id: int):
        from domain.enrollment.models import StudentEnrollment

        return StudentPayment.objects.filter(
            student_enrollment__classroom_id=classroom_id,
            is_deleted=False,
        ).select_related(
            "student_enrollment__student__user",
            "school_fee__fee_type",
        ).order_by("-payment_date")

    @staticmethod
    def list_by_school_year(school_year_id: int):
        return StudentPayment.objects.filter(
            school_fee__school_year_id=school_year_id,
            is_deleted=False,
        ).select_related(
            "student_enrollment__student__user",
            "school_fee__fee_type",
        ).order_by("-payment_date")
