from domain.finance.models import SchoolFee


class SchoolFeeSelector:
    @staticmethod
    def list_by_school_year(school_year_id: int):
        return SchoolFee.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        ).select_related("fee_type", "school_year_level", "school_year_cycle")

    @staticmethod
    def list_by_school_year_level(school_year_level_id: int):
        return SchoolFee.objects.filter(
            school_year_level_id=school_year_level_id, is_deleted=False
        ).select_related("fee_type")

    @staticmethod
    def get_by_id(school_fee_id: int):
        return SchoolFee.objects.filter(id=school_fee_id, is_deleted=False).first()

    @staticmethod
    def exists(
        *,
        school_year_id: int,
        school_year_level_id: int,
        fee_type_id: int,
        school_year_cycle_id=None,
    ):
        qs = SchoolFee.objects.filter(
            school_year_id=school_year_id,
            school_year_level_id=school_year_level_id,
            fee_type_id=fee_type_id,
            is_deleted=False,
        )
        if school_year_cycle_id is not None:
            qs = qs.filter(school_year_cycle_id=school_year_cycle_id)
        else:
            qs = qs.filter(school_year_cycle_id__isnull=True)
        return qs.exists()
