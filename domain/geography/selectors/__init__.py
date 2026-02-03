"""
Geography selectors.
"""

from domain.geography.selectors.country import CountrySelector
from domain.geography.selectors.region import RegionSelector
from domain.geography.selectors.administrative_unit import AdministrativeUnitSelector
from domain.geography.selectors.locality import LocalitySelector

__all__ = [
    'CountrySelector',
    'RegionSelector',
    'AdministrativeUnitSelector',
    'LocalitySelector',
]
