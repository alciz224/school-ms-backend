"""
Geography API views.
"""

from domain.geography.api.views.country import CountryViewSet
from domain.geography.api.views.region import RegionViewSet
from domain.geography.api.views.administrative_unit import AdministrativeUnitViewSet
from domain.geography.api.views.locality import LocalityViewSet

__all__ = [
    'CountryViewSet',
    'RegionViewSet',
    'AdministrativeUnitViewSet',
    'LocalityViewSet',
]
