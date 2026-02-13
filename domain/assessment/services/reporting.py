from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from django.db import transaction
from django.db.models import Avg, Q

from domain.assessment.models import ReportCard, ReportCardSubject, StudentAssessment, Transcript
from domain.enrollment.models import Classroom, StudentEnrollment
from domain.school_operations.models import SchoolYear, SchoolYearCycleTerm, SchoolYearLevelSubject
from domain.shared.exceptions import BusinessRuleException


@dataclass(frozen=True)
class ReportCardGenerationResult:
    report_cards_created: int
    report_cards_updated: int
    subjects_created: int


class ReportCardService:
    @staticmethod
    @transaction.atomic
    def generate_for_classroom_term(
        *,
        classroom: Classroom,
        term: SchoolYearCycleTerm,
        user=None,
        force: bool = False,
    ) -> ReportCardGenerationResult:
        """Generate report cards for a classroom + term.

        - Uses VALIDATED, non-absent grades only.
        - Weighted average by SchoolYearLevelSubject.coefficient.
        - Rank computed per classroom+term (ties share same rank).
        - If existing report card is final and force=False → error.
        """

        # Enrollments in classroom
        enrollments = list(
            StudentEnrollment.objects.filter(
                classroom_id=classroom.id,
                is_deleted=False,
            ).select_related("school_year_level")
        )
        if not enrollments:
            return ReportCardGenerationResult(0, 0, 0)

        # Ensure term belongs to same school year
        classroom_sy_id = classroom.school_year_level.school_year_cycle.school_year_id
        if term.school_year_cycle.school_year_id != classroom_sy_id:
            raise BusinessRuleException(
                rule="term_mismatch",
                message="Term does not belong to the same school year as the classroom.",
            )

        level_subjects = list(
            SchoolYearLevelSubject.objects.filter(
                school_year_level_id=classroom.school_year_level_id,
                is_deleted=False,
            ).select_related("subject")
        )
        level_subjects_by_id = {ls.id: ls for ls in level_subjects}

        # Aggregate averages per enrollment + subject for this term
        averages = (
            StudentAssessment.objects.filter(
                assessment_subject__classroom_id=classroom.id,
                assessment_subject__assessment__school_year_cycle_term_id=term.id,
                status="VALIDATED",
                is_absent=False,
                is_deleted=False,
            )
            .order_by()
            .values(
                "student_enrollment_id",
                "assessment_subject__school_year_level_subject_id",
            )
            .annotate(avg_raw=Avg("raw_score"))
        )

        avg_map: Dict[Tuple[int, int], Decimal] = {}
        for row in averages:
            avg_map[(row["student_enrollment_id"], row["assessment_subject__school_year_level_subject_id"])] = row[
                "avg_raw"
            ]

        # Prepare report cards (update existing or create new)
        report_cards_created = 0
        report_cards_updated = 0
        subjects_created = 0

        existing_rcs = ReportCard.objects.filter(
            student_enrollment_id__in=[e.id for e in enrollments],
            school_year_cycle_term_id=term.id,
            is_deleted=False,
        )
        existing_map = {rc.student_enrollment_id: rc for rc in existing_rcs}

        report_cards: List[ReportCard] = []
        subjects_to_create: List[ReportCardSubject] = []

        # Compute overall averages
        enrollment_averages: Dict[int, Decimal | None] = {}

        for e in enrollments:
            # Compute weighted average
            total_weight = Decimal("0")
            weighted_sum = Decimal("0")
            for ls in level_subjects:
                avg_val = avg_map.get((e.id, ls.id))
                if avg_val is not None:
                    coef = Decimal(ls.coefficient)
                    weighted_sum += Decimal(avg_val) * coef
                    total_weight += coef
            overall_avg = (weighted_sum / total_weight) if total_weight > 0 else None
            enrollment_averages[e.id] = overall_avg

        # Compute ranking (desc by average, None at bottom)
        sorted_enrollments = sorted(
            enrollments,
            key=lambda x: (-(enrollment_averages[x.id] or Decimal("-1"))),
        )
        rank_map: Dict[int, int | None] = {}
        last_avg = None
        current_rank = 0
        for idx, e in enumerate(sorted_enrollments, start=1):
            avg = enrollment_averages[e.id]
            if avg is None:
                rank_map[e.id] = None
                continue
            if last_avg is None or avg != last_avg:
                current_rank = idx
                last_avg = avg
            rank_map[e.id] = current_rank

        for e in enrollments:
            existing = existing_map.get(e.id)
            if existing and existing.is_final and not force:
                raise BusinessRuleException(
                    rule="report_card_locked",
                    message="Report card is final and cannot be regenerated.",
                )

            if existing:
                # Clear existing subjects and update report card
                ReportCardSubject.objects.filter(report_card_id=existing.id).delete()
                existing.overall_average = enrollment_averages[e.id]
                existing.rank = rank_map[e.id]
                existing.classroom = classroom
                existing.is_final = True
                existing.raw_data = {
                    "overall_average": str(enrollment_averages[e.id]) if enrollment_averages[e.id] is not None else None,
                    "rank": rank_map[e.id],
                }
                existing.save_by(user=user)
                report_cards_updated += 1
                rc = existing
            else:
                rc = ReportCard(
                    student_enrollment=e,
                    school_year_cycle_term=term,
                    classroom=classroom,
                    overall_average=enrollment_averages[e.id],
                    rank=rank_map[e.id],
                    is_final=True,
                    raw_data={
                        "overall_average": str(enrollment_averages[e.id]) if enrollment_averages[e.id] is not None else None,
                        "rank": rank_map[e.id],
                    },
                    created_by=user,
                    updated_by=user,
                )
                report_cards.append(rc)
                report_cards_created += 1

        if report_cards:
            ReportCard.objects.bulk_create(report_cards)

        # Build ReportCardSubject rows
        # Refresh newly created report cards
        if report_cards_created:
            created_rcs = ReportCard.objects.filter(
                student_enrollment_id__in=[e.id for e in enrollments],
                school_year_cycle_term_id=term.id,
                is_deleted=False,
            )
            for rc in created_rcs:
                existing_map[rc.student_enrollment_id] = rc

        for e in enrollments:
            rc = existing_map[e.id]
            for ls in level_subjects:
                avg_val = avg_map.get((e.id, ls.id))
                subjects_to_create.append(
                    ReportCardSubject(
                        report_card=rc,
                        school_year_level_subject=ls,
                        average=avg_val,
                        coefficient=ls.coefficient,
                        teacher_name="",
                    )
                )

        if subjects_to_create:
            ReportCardSubject.objects.bulk_create(subjects_to_create, batch_size=500)
            subjects_created = len(subjects_to_create)

        return ReportCardGenerationResult(
            report_cards_created=report_cards_created,
            report_cards_updated=report_cards_updated,
            subjects_created=subjects_created,
        )


class TranscriptService:
    @staticmethod
    @transaction.atomic
    def generate_for_student(*, student_enrollment: StudentEnrollment, school_year: SchoolYear, user=None) -> Transcript:
        """Generate transcript for a student based on finalized report cards."""
        report_cards = ReportCard.objects.filter(
            student_enrollment_id=student_enrollment.id,
            school_year_cycle_term__school_year_cycle__school_year_id=school_year.id,
            is_deleted=False,
        ).order_by("school_year_cycle_term__start_date")

        if not report_cards:
            raise BusinessRuleException(rule="no_report_cards", message="No report cards to aggregate.")

        # Average of term averages (ignore None)
        values = [rc.overall_average for rc in report_cards if rc.overall_average is not None]
        overall_avg = None
        if values:
            overall_avg = sum(values) / Decimal(len(values))

        transcript, _ = Transcript.objects.update_or_create(
            student_enrollment=student_enrollment,
            school_year=school_year,
            defaults={
                "overall_average": overall_avg,
                "raw_data": {"term_averages": [str(v) for v in values]},
                "updated_by": user,
            },
        )
        return transcript
