from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum, Q

from domain.finance.constants import PaymentStatus
from domain.finance.models import SchoolFee, StudentPayment


class FeeSummarySelector:
    @staticmethod
    def get_summaries(*, school_year_id: int, classroom_id: int = None):
        fees = SchoolFee.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        ).prefetch_related(
            "payments",
            "payments__student_enrollment__student__user",
        ).select_related("school_year_level")

        if classroom_id:
            from domain.enrollment.models import StudentEnrollment

            enrollments = StudentEnrollment.objects.filter(
                classroom_id=classroom_id, is_deleted=False
            ).values_list("id", flat=True)
            fees = fees.filter(payments__student_enrollment_id__in=enrollments)

        student_totals = defaultdict(lambda: {"total_due": Decimal("0.00"), "total_paid": Decimal("0.00")})

        for fee in fees:
            payments = fee.payments.filter(is_deleted=False)
            for payment in payments:
                key = payment.student_enrollment_id
                student_totals[key]["total_due"] += fee.amount
                student_totals[key]["total_paid"] += payment.amount_paid

        summaries = []
        for enrollment_id, totals in student_totals.items():
            balance = totals["total_due"] - totals["total_paid"]
            if balance <= 0:
                status = PaymentStatus.PAID
            elif totals["total_paid"] > 0:
                status = PaymentStatus.PARTIAL
            else:
                status = PaymentStatus.PENDING

            from domain.enrollment.models import StudentEnrollment

            enrollment = StudentEnrollment.objects.select_related(
                "student__user", "classroom"
            ).filter(id=enrollment_id).first()
            if not enrollment:
                continue

            summaries.append({
                "student_id": str(enrollment.student_id),
                "student_name": str(enrollment.student),
                "class_name": enrollment.classroom.name if enrollment.classroom else "",
                "level": str(enrollment.classroom.school_year_level.level if enrollment.classroom else ""),
                "total_due": float(totals["total_due"]),
                "total_paid": float(totals["total_paid"]),
                "balance": float(balance),
                "status": status,
                "last_payment_date": None,
            })

        return summaries

    @staticmethod
    def get_stats(*, school_year_id: int):
        fees = SchoolFee.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        )

        total_expected = fees.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        payments = StudentPayment.objects.filter(
            school_fee__school_year_id=school_year_id, is_deleted=False
        )
        total_collected = payments.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0.00")

        total_pending = total_expected - total_collected

        from domain.enrollment.models import StudentEnrollment

        school_years = SchoolFee.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        ).values_list("school_year_level", flat=True).distinct()

        students_count = StudentEnrollment.objects.filter(
            classroom__school_year_level_id__in=school_years,
            is_deleted=False,
        ).count()

        students_paid = (
            StudentPayment.objects.filter(
                school_fee__school_year_id=school_year_id, is_deleted=False
            )
            .values("student_enrollment")
            .distinct()
            .count()
        )

        students_pending = students_count - students_paid

        collection_rate = (
            float(total_collected) / float(total_expected) * 100
            if total_expected > 0
            else 0.0
        )

        return {
            "total_expected": float(total_expected),
            "total_collected": float(total_collected),
            "total_pending": float(total_pending),
            "total_overdue": 0.0,
            "collection_rate": round(collection_rate, 2),
            "students_count": students_count,
            "students_paid": students_paid,
            "students_pending": students_pending,
        }
