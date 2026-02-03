"""Seed reference geography data.

Currently seeds:
- Country: Guinea (GN)
- Regions: 8 administrative regions

The command is idempotent and restores soft-deleted records.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand
from django.db import transaction

from domain.geography.constants import AdministrativeUnitType
from domain.geography.models import (
    AdministrativeUnit,
    Country,
    Locality,
    RegionAdministrative,
)


@dataclass(frozen=True)
class RegionSeed:
    code: str
    name: str


GUINEA = {
    "code": "GN",
    "name": "Guinée",
    "description": "République de Guinée",
}

# 8 régions administratives de la Guinée (niveau officiel et stable)
GUINEA_REGIONS: list[RegionSeed] = [
    RegionSeed(code="BOKE", name="Boké"),
    RegionSeed(code="CON", name="Conakry"),
    RegionSeed(code="FAR", name="Faranah"),
    RegionSeed(code="KAN", name="Kankan"),
    RegionSeed(code="KIN", name="Kindia"),
    RegionSeed(code="LAB", name="Labé"),
    RegionSeed(code="MAM", name="Mamou"),
    RegionSeed(code="NZR", name="Nzérékoré"),
]


class Command(BaseCommand):
    help = "Seed geography reference data (GN + regions)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created/updated without writing to the DB.",
        )
        parser.add_argument(
            "--with-test-data",
            action="store_true",
            default=False,
            help="Also seed technical (TEST_*) AdministrativeUnits (and optionally Localities) per region.",
        )
        parser.add_argument(
            "--with-test-localities",
            action="store_true",
            default=False,
            help="When used with --with-test-data, also create 1-2 Locality rows per region.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        with_test_data: bool = options["with_test_data"]
        with_test_localities: bool = options["with_test_localities"]

        if dry_run:
            self.stdout.write(self.style.WARNING("Running in --dry-run mode (no DB writes)."))

        with transaction.atomic():
            country, country_action = self._upsert_country(dry_run=dry_run)
            regions_actions = self._upsert_regions(country=country, dry_run=dry_run)

            units_actions: list[tuple[str, str, str]] = []
            localities_actions: list[tuple[str, str, str]] = []

            if with_test_data:
                units_actions = self._seed_test_units(country=country, dry_run=dry_run)
                if with_test_localities:
                    localities_actions = self._seed_test_localities(country=country, dry_run=dry_run)

            if dry_run:
                # Rollback everything
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"Country: {country.code} - {country.name} ({country_action})"))
        for code, name, action in regions_actions:
            self.stdout.write(self.style.SUCCESS(f"Region: {code} - {name} ({action})"))
        for code, name, action in units_actions:
            self.stdout.write(self.style.SUCCESS(f"AdminUnit: {code} - {name} ({action})"))
        for code, name, action in localities_actions:
            self.stdout.write(self.style.SUCCESS(f"Locality: {code} - {name} ({action})"))

    def _restore_if_deleted(self, obj) -> bool:
        """Restore a soft-deleted object. Returns True if restored."""
        restored = False
        if getattr(obj, "is_deleted", False):
            obj.is_deleted = False
            obj.deleted_at = None
            obj.deleted_by = None
            restored = True
        return restored

    def _upsert_country(self, *, dry_run: bool) -> tuple[Country, str]:
        # Use all_objects to find even soft-deleted rows.
        country = Country.all_objects.filter(code=GUINEA["code"]).first()
        action = "unchanged"

        if country is None:
            country = Country(code=GUINEA["code"], name=GUINEA["name"], description=GUINEA["description"])  # type: ignore[call-arg]
            action = "created"
            # Even in --dry-run, save inside the atomic transaction so the instance has a PK
            # (we rollback at the end of handle()).
            country.save()
            return country, action

        restored = self._restore_if_deleted(country)

        changed = False
        if country.name != GUINEA["name"]:
            country.name = GUINEA["name"]
            changed = True
        if country.description != GUINEA["description"]:
            country.description = GUINEA["description"]
            changed = True

        if restored:
            changed = True

        if changed:
            action = "restored" if restored else "updated"
            if not dry_run:
                country.save()

        return country, action

    def _upsert_regions(self, *, country: Country, dry_run: bool) -> list[tuple[str, str, str]]:
        results: list[tuple[str, str, str]] = []

        for seed in GUINEA_REGIONS:
            region = RegionAdministrative.all_objects.filter(country=country, code=seed.code).first()
            action = "unchanged"

            if region is None:
                region = RegionAdministrative(country=country, code=seed.code, name=seed.name)  # type: ignore[call-arg]
                action = "created"
                # Even in --dry-run, save inside the atomic transaction so the instance has a PK
                # (we rollback at the end of handle()).
                region.save()
                results.append((seed.code, seed.name, action))
                continue

            restored = self._restore_if_deleted(region)

            changed = False
            if region.name != seed.name:
                region.name = seed.name
                changed = True

            # Keep codes stable (do not change seed.code)
            if restored:
                changed = True

            if changed:
                action = "restored" if restored else "updated"
                region.save()

            results.append((seed.code, seed.name, action))

        return results

    def _upsert_unit(
        self,
        *,
        region: RegionAdministrative,
        code: str,
        name: str,
        unit_type: str,
        parent: AdministrativeUnit | None = None,
    ) -> tuple[AdministrativeUnit, str]:
        unit = AdministrativeUnit.all_objects.filter(region=region, code=code).first()
        action = "unchanged"

        if unit is None:
            unit = AdministrativeUnit(
                region=region,
                code=code,
                name=name,
                type=unit_type,
                parent=parent,
            )  # type: ignore[call-arg]
            unit.save()
            return unit, "created"

        restored = self._restore_if_deleted(unit)

        changed = False
        if unit.name != name:
            unit.name = name
            changed = True
        if unit.type != unit_type:
            unit.type = unit_type
            changed = True
        # Parent can be NULL or a FK; keep it aligned with the seed.
        if (unit.parent_id or None) != (parent.id if parent else None):
            unit.parent = parent
            changed = True

        if restored:
            changed = True

        if changed:
            action = "restored" if restored else "updated"
            unit.save()

        return unit, action

    def _upsert_locality(
        self,
        *,
        code: str,
        name: str,
        administrative_unit: AdministrativeUnit,
    ) -> tuple[Locality, str]:
        loc = Locality.all_objects.filter(administrative_unit=administrative_unit, code=code).first()
        action = "unchanged"

        if loc is None:
            loc = Locality(
                code=code,
                name=name,
                administrative_unit=administrative_unit,
            )  # type: ignore[call-arg]
            loc.save()
            return loc, "created"

        restored = self._restore_if_deleted(loc)

        changed = False
        if loc.name != name:
            loc.name = name
            changed = True
        # administrative_unit is part of the natural key here; we don't support moving a locality
        # between administrative units automatically.

        if restored:
            changed = True

        if changed:
            action = "restored" if restored else "updated"
            loc.save()

        return loc, action

    def _seed_test_units(self, *, country: Country, dry_run: bool) -> list[tuple[str, str, str]]:
        """Create a minimal but coherent TEST_* dataset for each seeded region.

        For each region:
        - 1 PREFECTURE (no parent)
        - 1 SUBPREFECTURE (parent=the prefecture)
        - 1 COMMUNE (no parent)
        """

        results: list[tuple[str, str, str]] = []

        regions = RegionAdministrative.objects.filter(country=country, is_deleted=False)
        for region in regions:
            pref_code = f"TEST_{region.code}_PREF"
            subpref_code = f"TEST_{region.code}_SUBPREF"
            commune_code = f"TEST_{region.code}_COMM"

            prefecture, action = self._upsert_unit(
                region=region,
                code=pref_code,
                name=f"Test Prefecture {region.name}",
                unit_type=AdministrativeUnitType.PREFECTURE,
                parent=None,
            )
            results.append((pref_code, prefecture.name, action))

            subpref, action = self._upsert_unit(
                region=region,
                code=subpref_code,
                name=f"Test Subprefecture {region.name}",
                unit_type=AdministrativeUnitType.SUBPREFECTURE,
                parent=prefecture,
            )
            results.append((subpref_code, subpref.name, action))

            commune, action = self._upsert_unit(
                region=region,
                code=commune_code,
                name=f"Test Commune {region.name}",
                unit_type=AdministrativeUnitType.COMMUNE,
                parent=None,
            )
            results.append((commune_code, commune.name, action))

        return results

    def _seed_test_localities(self, *, country: Country, dry_run: bool) -> list[tuple[str, str, str]]:
        """Create a minimal TEST_* Locality dataset for each region.

        Creates 2 localities per region:
        - One attached to the region's TEST commune
        - One attached to the region's TEST subprefecture
        """

        results: list[tuple[str, str, str]] = []

        regions = RegionAdministrative.objects.filter(country=country, is_deleted=False)
        for region in regions:
            commune = AdministrativeUnit.objects.filter(
                region=region,
                code=f"TEST_{region.code}_COMM",
                is_deleted=False,
            ).first()
            subpref = AdministrativeUnit.objects.filter(
                region=region,
                code=f"TEST_{region.code}_SUBPREF",
                is_deleted=False,
            ).first()

            # If units weren't seeded (or were manually deleted), skip gracefully.
            if commune is None or subpref is None:
                continue

            loc1_code = f"TEST_{region.code}_LOC1"
            loc2_code = f"TEST_{region.code}_LOC2"

            loc1, action = self._upsert_locality(
                code=loc1_code,
                name=f"Test Locality 1 ({region.name})",
                administrative_unit=commune,
            )
            results.append((loc1_code, loc1.name, action))

            loc2, action = self._upsert_locality(
                code=loc2_code,
                name=f"Test Locality 2 ({region.name})",
                administrative_unit=subpref,
            )
            results.append((loc2_code, loc2.name, action))

        return results
