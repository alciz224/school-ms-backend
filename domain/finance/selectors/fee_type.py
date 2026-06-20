from domain.finance.models import FeeType


class FeeTypeSelector:
    @staticmethod
    def list_active():
        return FeeType.objects.filter(is_deleted=False, is_active=True).order_by("category", "name")

    @staticmethod
    def list_all():
        return FeeType.objects.filter(is_deleted=False).order_by("category", "name")

    @staticmethod
    def get_by_id(fee_type_id: int):
        return FeeType.objects.filter(id=fee_type_id, is_deleted=False).first()
