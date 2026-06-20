from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from domain.finance.api.serializers.fee_type import FeeTypeSerializer
from domain.finance.models import FeeType
from domain.finance.selectors.fee_type import FeeTypeSelector


class FeeTypeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FeeTypeSerializer

    def get_queryset(self):
        return FeeTypeSelector.list_active()
