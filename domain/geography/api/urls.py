"""
Geography API URL configuration.

All geography URLs are registered at root level without the app name prefix:
- /api/v1/countries/
- /api/v1/regions/
- /api/v1/administrative-units/
- /api/v1/localities/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.geography.api.views import (
    CountryViewSet,
    RegionViewSet,
    AdministrativeUnitViewSet,
    LocalityViewSet,
)

app_name = 'geography'

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'administrative-units', AdministrativeUnitViewSet, basename='administrative-unit')
router.register(r'localities', LocalityViewSet, basename='locality')

urlpatterns = router.urls
