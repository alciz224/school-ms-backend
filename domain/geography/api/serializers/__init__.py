"""
Geography API serializers.
"""

from domain.geography.api.serializers.country import (
    CountryListSerializer,
    CountryDetailSerializer,
    CountryCreateSerializer,
    CountryUpdateSerializer,
)
from domain.geography.api.serializers.region import (
    RegionListSerializer,
    RegionDetailSerializer,
    RegionCreateSerializer,
    RegionUpdateSerializer,
)
from domain.geography.api.serializers.administrative_unit import (
    AdministrativeUnitListSerializer,
    AdministrativeUnitDetailSerializer,
    AdministrativeUnitCreateSerializer,
    AdministrativeUnitUpdateSerializer,
)
from domain.geography.api.serializers.locality import (
    LocalityListSerializer,
    LocalityDetailSerializer,
    LocalityCreateSerializer,
    LocalityUpdateSerializer,
)

__all__ = [
    # Country
    'CountryListSerializer',
    'CountryDetailSerializer',
    'CountryCreateSerializer',
    'CountryUpdateSerializer',
    # Region
    'RegionListSerializer',
    'RegionDetailSerializer',
    'RegionCreateSerializer',
    'RegionUpdateSerializer',
    # Administrative Unit
    'AdministrativeUnitListSerializer',
    'AdministrativeUnitDetailSerializer',
    'AdministrativeUnitCreateSerializer',
    'AdministrativeUnitUpdateSerializer',
    # Locality
    'LocalityListSerializer',
    'LocalityDetailSerializer',
    'LocalityCreateSerializer',
    'LocalityUpdateSerializer',
]
