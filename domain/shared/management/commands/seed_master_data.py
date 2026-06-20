"""
Seed des données master (référence) pour le contexte éducatif guinéen.

Périmètre :
    - Géographie : Pays (Guinée) + 8 régions administratives + 33 préfectures
      + 5 communes urbaines de Conakry + sous-préfectures principales + localités
    - Académique : Cycles MEN-Guinée (Maternelle, Primaire, Collège, Lycée)
      avec niveaux, filières, matières, types d'évaluation et périodes
    - Finance : Types de frais standards (inscription, scolarité, examens...)
    - Année académique : Année courante créée et marquée ACTIVE

Idempotent : safe à relancer (get_or_create partout).

Usage :
    python manage.py seed_master_data
    python manage.py seed_master_data --skip-finance
    python manage.py seed_master_data --year 2025
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from domain.academic.models import (
    AcademicYear,
    AssessmentType,
    Cycle,
    Level,
    Subject,
    Term,
    TermType,
    Track,
)
from domain.finance.constants import FeeCategory, PaymentFrequency
from domain.finance.models import FeeType
from domain.geography.constants import AdministrativeUnitType
from domain.geography.models import (
    AdministrativeUnit,
    Country,
    Locality,
    RegionAdministrative,
)


# =============================================================================
# GÉOGRAPHIE — République de Guinée
# =============================================================================

GUINEA = {"code": "GN", "name": "Guinée", "description": "République de Guinée"}


@dataclass(frozen=True)
class RegionSeed:
    code: str
    name: str


@dataclass(frozen=True)
class PrefectureSeed:
    region_code: str
    code: str
    name: str


@dataclass(frozen=True)
class CommuneSeed:
    region_code: str
    code: str
    name: str


@dataclass(frozen=True)
class SubprefectureSeed:
    region_code: str
    prefecture_code: str
    code: str
    name: str


@dataclass(frozen=True)
class LocalitySeed:
    region_code: str
    unit_code: str
    code: str
    name: str


# 8 régions administratives + Conakry (zone spéciale)
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

# 33 préfectures (officielles, hors Conakry qui est divisée en communes)
GUINEA_PREFECTURES: list[PrefectureSeed] = [
    # Boké (5)
    PrefectureSeed("BOKE", "BOKE_P", "Boké"),
    PrefectureSeed("BOKE", "BOFFA", "Boffa"),
    PrefectureSeed("BOKE", "FRIA", "Fria"),
    PrefectureSeed("BOKE", "GAOUAL", "Gaoual"),
    PrefectureSeed("BOKE", "KOUNDARA", "Koundara"),
    # Faranah (4)
    PrefectureSeed("FAR", "FAR_P", "Faranah"),
    PrefectureSeed("FAR", "DABOLA", "Dabola"),
    PrefectureSeed("FAR", "DINGUIRAYE", "Dinguiraye"),
    PrefectureSeed("FAR", "KISSIDOUGOU", "Kissidougou"),
    # Kankan (5)
    PrefectureSeed("KAN", "KAN_P", "Kankan"),
    PrefectureSeed("KAN", "KEROUANE", "Kérouané"),
    PrefectureSeed("KAN", "KOUROUSSA", "Kouroussa"),
    PrefectureSeed("KAN", "MANDIANA", "Mandiana"),
    PrefectureSeed("KAN", "SIGUIRI", "Siguiri"),
    # Kindia (5)
    PrefectureSeed("KIN", "KIN_P", "Kindia"),
    PrefectureSeed("KIN", "COYAH", "Coyah"),
    PrefectureSeed("KIN", "DUBREKA", "Dubréka"),
    PrefectureSeed("KIN", "FORECARIAH", "Forécariah"),
    PrefectureSeed("KIN", "TELIMELE", "Télimélé"),
    # Labé (5)
    PrefectureSeed("LAB", "LAB_P", "Labé"),
    PrefectureSeed("LAB", "KOUBIA", "Koubia"),
    PrefectureSeed("LAB", "LELOUMA", "Lélouma"),
    PrefectureSeed("LAB", "MALI", "Mali"),
    PrefectureSeed("LAB", "TOUGUE", "Tougué"),
    # Mamou (3)
    PrefectureSeed("MAM", "MAM_P", "Mamou"),
    PrefectureSeed("MAM", "DALABA", "Dalaba"),
    PrefectureSeed("MAM", "PITA", "Pita"),
    # Nzérékoré (6)
    PrefectureSeed("NZR", "NZR_P", "Nzérékoré"),
    PrefectureSeed("NZR", "BEYLA", "Beyla"),
    PrefectureSeed("NZR", "GUECKEDOU", "Guéckédou"),
    PrefectureSeed("NZR", "LOLA", "Lola"),
    PrefectureSeed("NZR", "MACENTA", "Macenta"),
    PrefectureSeed("NZR", "YOMOU", "Yomou"),
]

# 5 communes urbaines de Conakry
CONAKRY_COMMUNES: list[CommuneSeed] = [
    CommuneSeed("CON", "KALOUM", "Kaloum"),
    CommuneSeed("CON", "DIXINN", "Dixinn"),
    CommuneSeed("CON", "MATAM", "Matam"),
    CommuneSeed("CON", "MATOTO", "Matoto"),
    CommuneSeed("CON", "RATOMA", "Ratoma"),
]

# Échantillon de sous-préfectures (capitales économiques connues)
GUINEA_SUBPREFECTURES: list[SubprefectureSeed] = [
    SubprefectureSeed("BOKE", "BOKE_P", "KAMSAR", "Kamsar"),
    SubprefectureSeed("BOKE", "BOKE_P", "SANGAREDI", "Sangarédi"),
    SubprefectureSeed("BOKE", "BOFFA", "TAMITA", "Tamita"),
    SubprefectureSeed("KIN", "COYAH", "MANEAH", "Manéah"),
    SubprefectureSeed("KIN", "DUBREKA", "TANENE", "Tanéné"),
    SubprefectureSeed("KAN", "SIGUIRI", "DOKO", "Doko"),
    SubprefectureSeed("KAN", "SIGUIRI", "NIANDANKORO", "Niandankoro"),
    SubprefectureSeed("NZR", "MACENTA", "DARO", "Daro"),
    SubprefectureSeed("MAM", "PITA", "BANTIGNEL", "Bantignel"),
    SubprefectureSeed("FAR", "FAR_P", "BEINDOU", "Beindou"),
]

# Échantillon de localités (chef-lieux et quartiers connus)
GUINEA_LOCALITIES: list[LocalitySeed] = [
    # Boké
    LocalitySeed("BOKE", "BOKE_P", "BOKE_C", "Boké Centre"),
    LocalitySeed("BOKE", "KAMSAR", "KAMSAR_C", "Kamsar Centre"),
    # Conakry — quartiers principaux
    LocalitySeed("CON", "KALOUM", "ALMAMYA", "Almamya"),
    LocalitySeed("CON", "KALOUM", "BOULBINET", "Boulbinet"),
    LocalitySeed("CON", "DIXINN", "DIXINN_C", "Dixinn Centre"),
    LocalitySeed("CON", "DIXINN", "MINIERE", "Minière"),
    LocalitySeed("CON", "MATAM", "MATAM_C", "Matam Centre"),
    LocalitySeed("CON", "MATAM", "COLEAH", "Coléah"),
    LocalitySeed("CON", "MATOTO", "MATOTO_C", "Matoto Centre"),
    LocalitySeed("CON", "MATOTO", "TOMBOLIA", "Tombolia"),
    LocalitySeed("CON", "RATOMA", "RATOMA_C", "Ratoma Centre"),
    LocalitySeed("CON", "RATOMA", "KIPE", "Kipé"),
    LocalitySeed("CON", "RATOMA", "LAMBANYI", "Lambanyi"),
    # Kankan
    LocalitySeed("KAN", "KAN_P", "KANKAN_C", "Kankan Centre"),
    LocalitySeed("KAN", "SIGUIRI", "SIGUIRI_C", "Siguiri Centre"),
    # Nzérékoré
    LocalitySeed("NZR", "NZR_P", "NZR_C", "Nzérékoré Centre"),
    LocalitySeed("NZR", "GUECKEDOU", "GUECKEDOU_C", "Guéckédou Centre"),
    # Kindia
    LocalitySeed("KIN", "KIN_P", "KINDIA_C", "Kindia Centre"),
    # Labé
    LocalitySeed("LAB", "LAB_P", "LABE_C", "Labé Centre"),
    # Mamou
    LocalitySeed("MAM", "MAM_P", "MAMOU_C", "Mamou Centre"),
    # Faranah
    LocalitySeed("FAR", "FAR_P", "FARANAH_C", "Faranah Centre"),
]


# =============================================================================
# ACADÉMIQUE — Système MEN Guinée
# =============================================================================

# Cycles éducatifs (MEN-Guinée)
CYCLES = [
    {"code": "MAT", "name": "Maternelle", "has_track": False},
    {"code": "PRI", "name": "Primaire", "has_track": False},
    {"code": "COL", "name": "Collège", "has_track": False},
    {"code": "LYC", "name": "Lycée", "has_track": True},
]

# Filières du Lycée
LYCEE_TRACKS = [
    {"code": "SM", "name": "Sciences Mathématiques"},
    {"code": "SE", "name": "Sciences Expérimentales"},
    {"code": "SS", "name": "Sciences Sociales"},
]

# Niveaux Maternelle (Préscolaire guinéen)
MAT_LEVELS = [
    {"code": "PS", "name": "Petite Section", "order": 1},
    {"code": "MS", "name": "Moyenne Section", "order": 2},
    {"code": "GS", "name": "Grande Section", "order": 3},
]

# Niveaux Primaire (système guinéen : 1ère à 6ème année)
PRI_LEVELS = [
    {"code": "1A", "name": "1ère Année (CP1)", "order": 1},
    {"code": "2A", "name": "2ème Année (CP2)", "order": 2},
    {"code": "3A", "name": "3ème Année (CE1)", "order": 3},
    {"code": "4A", "name": "4ème Année (CE2)", "order": 4},
    {"code": "5A", "name": "5ème Année (CM1)", "order": 5},
    {"code": "6A", "name": "6ème Année (CM2)", "order": 6},
]

# Niveaux Collège (Guinée : 7ème à 10ème, fin avec BEPC)
COL_LEVELS = [
    {"code": "7EME", "name": "7ème Année", "order": 1},
    {"code": "8EME", "name": "8ème Année", "order": 2},
    {"code": "9EME", "name": "9ème Année", "order": 3},
    {"code": "10EME", "name": "10ème Année", "order": 4},
]

# Niveaux Lycée (avec filières) — 11ème, 12ème, Terminale × {SM, SE, SS}
LYC_LEVELS_TEMPLATE = [
    {"code": "11EME", "name": "11ème", "order": 1},
    {"code": "12EME", "name": "12ème", "order": 2},
    {"code": "TER", "name": "Terminale", "order": 3},
]

# Matières (programme officiel guinéen — global)
SUBJECTS = [
    # Tronc commun
    {"code": "FRAN", "name": "Français"},
    {"code": "MATH", "name": "Mathématiques"},
    {"code": "ANG", "name": "Anglais"},
    {"code": "HG", "name": "Histoire-Géographie"},
    {"code": "ECM", "name": "Éducation Civique et Morale"},
    {"code": "EPS", "name": "Éducation Physique et Sportive"},
    {"code": "ARABE", "name": "Arabe"},
    # Sciences
    {"code": "SVT", "name": "Sciences de la Vie et de la Terre"},
    {"code": "PHYS", "name": "Sciences Physiques"},
    {"code": "CHIM", "name": "Chimie"},
    {"code": "BIO", "name": "Biologie"},
    # Primaire spécifique
    {"code": "EVEIL", "name": "Éveil Scientifique"},
    {"code": "LECT", "name": "Lecture-Écriture"},
    {"code": "CALC", "name": "Calcul"},
    # Lycée spécifique
    {"code": "PHILO", "name": "Philosophie"},
    {"code": "ECO", "name": "Économie"},
    {"code": "INFO", "name": "Informatique"},
    # Artistiques / facultatives
    {"code": "ART", "name": "Arts Plastiques"},
    {"code": "MUS", "name": "Musique"},
]

# Types d'évaluation (calendrier scolaire guinéen)
ASSESSMENT_TYPES = [
    {"code": "INTER", "name": "Interrogation",
     "description": "Évaluation courte et fréquente en classe."},
    {"code": "DEVOIR", "name": "Devoir surveillé",
     "description": "Devoir en classe sur une période définie."},
    {"code": "COMPO", "name": "Composition",
     "description": "Évaluation formelle de fin de trimestre."},
    {"code": "EXAM_BLANC", "name": "Examen Blanc",
     "description": "Simulation d'examen officiel (BEPC/BAC) avant la session."},
    {"code": "BEPC", "name": "BEPC",
     "description": "Brevet d'Études du Premier Cycle (fin 10ème année)."},
    {"code": "BAC", "name": "Baccalauréat",
     "description": "Examen de fin de Terminale, certifié par le MEN."},
    {"code": "TP", "name": "Travaux Pratiques",
     "description": "Évaluation de manipulations en laboratoire."},
]

# Type de découpage temporel (Guinée : trimestrielle dominante)
TERM_TYPES = [
    {"code": "TRIMESTER", "name": "Trimestre", "period_count": 3},
    {"code": "SEMESTER", "name": "Semestre", "period_count": 2},
]

TRIMESTER_TERMS = [
    {"code": "T1", "name": "Trimestre 1", "order": 1},
    {"code": "T2", "name": "Trimestre 2", "order": 2},
    {"code": "T3", "name": "Trimestre 3", "order": 3},
]

SEMESTER_TERMS = [
    {"code": "S1", "name": "Semestre 1", "order": 1},
    {"code": "S2", "name": "Semestre 2", "order": 2},
]


# =============================================================================
# FINANCE — Types de frais (référentiel)
# =============================================================================

FEE_TYPES = [
    {
        "name": "Frais d'inscription",
        "category": FeeCategory.REGISTRATION,
        "default_amount": Decimal("50000"),
        "payment_frequency": PaymentFrequency.ANNUAL,
        "description": "Frais d'inscription annuels (rentrée scolaire).",
    },
    {
        "name": "Scolarité trimestrielle",
        "category": FeeCategory.TUITION,
        "default_amount": Decimal("150000"),
        "payment_frequency": PaymentFrequency.TERM,
        "description": "Frais de scolarité dus chaque trimestre.",
    },
    {
        "name": "Scolarité mensuelle",
        "category": FeeCategory.TUITION,
        "default_amount": Decimal("50000"),
        "payment_frequency": PaymentFrequency.MONTHLY,
        "description": "Frais de scolarité mensuels (option de paiement étalé).",
    },
    {
        "name": "Tenue scolaire",
        "category": FeeCategory.MATERIAL,
        "default_amount": Decimal("75000"),
        "payment_frequency": PaymentFrequency.ANNUAL,
        "description": "Uniforme et fournitures de base.",
    },
    {
        "name": "Frais d'examen BEPC",
        "category": FeeCategory.EXAM,
        "default_amount": Decimal("25000"),
        "payment_frequency": PaymentFrequency.ANNUAL,
        "description": "Frais d'inscription à l'examen national du BEPC.",
    },
    {
        "name": "Frais d'examen BAC",
        "category": FeeCategory.EXAM,
        "default_amount": Decimal("35000"),
        "payment_frequency": PaymentFrequency.ANNUAL,
        "description": "Frais d'inscription à l'examen national du Baccalauréat.",
    },
    {
        "name": "Transport scolaire",
        "category": FeeCategory.TRANSPORT,
        "default_amount": Decimal("30000"),
        "payment_frequency": PaymentFrequency.MONTHLY,
        "description": "Service de transport scolaire (optionnel).",
    },
    {
        "name": "Cantine",
        "category": FeeCategory.MEAL,
        "default_amount": Decimal("20000"),
        "payment_frequency": PaymentFrequency.MONTHLY,
        "description": "Restauration scolaire (déjeuner).",
    },
    {
        "name": "Cotisation APE",
        "category": FeeCategory.PTA,
        "default_amount": Decimal("10000"),
        "payment_frequency": PaymentFrequency.ANNUAL,
        "description": "Cotisation à l'Association des Parents d'Élèves.",
    },
]


# =============================================================================
# COMMANDE
# =============================================================================


class Command(BaseCommand):
    help = (
        "Seed des données master pour l'éducation guinéenne : "
        "géographie (Guinée + régions + préfectures + communes Conakry), "
        "système académique MEN, types d'évaluation, périodes, et frais."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Année académique courante à créer (ex. 2025 pour 2025-2026). "
                 "Par défaut : année calendaire actuelle.",
        )
        parser.add_argument(
            "--skip-geography",
            action="store_true",
            help="Ne pas seeder la géographie.",
        )
        parser.add_argument(
            "--skip-academic",
            action="store_true",
            help="Ne pas seeder le système académique.",
        )
        parser.add_argument(
            "--skip-finance",
            action="store_true",
            help="Ne pas seeder les types de frais.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            ">> Seed des donnees master (contexte educatif guineen)"
        ))

        with transaction.atomic():
            if not options["skip_geography"]:
                self.stdout.write(self.style.MIGRATE_LABEL("\n[1/4] Géographie"))
                self._seed_geography()

            if not options["skip_academic"]:
                self.stdout.write(self.style.MIGRATE_LABEL("\n[2/4] Système académique"))
                self._seed_academic()
                self.stdout.write(self.style.MIGRATE_LABEL("\n[3/4] Année académique"))
                self._seed_academic_year(start_year=options["year"])

            if not options["skip_finance"]:
                self.stdout.write(self.style.MIGRATE_LABEL("\n[4/4] Types de frais"))
                self._seed_finance()

        self.stdout.write(self.style.SUCCESS("\n[OK] Seed termine avec succes."))

    # -------------------------------------------------------------------------
    # Géographie
    # -------------------------------------------------------------------------

    def _seed_geography(self):
        # Pays
        country, created = Country.objects.get_or_create(
            code=GUINEA["code"],
            defaults={"name": GUINEA["name"], "description": GUINEA["description"]},
        )
        self._log("Pays", country, created)

        # Régions
        regions_by_code: dict[str, RegionAdministrative] = {}
        for r in GUINEA_REGIONS:
            region, created = RegionAdministrative.objects.get_or_create(
                country=country,
                code=r.code,
                defaults={"name": r.name},
            )
            regions_by_code[r.code] = region
            self._log("Région", region, created, indent=1)

        # Préfectures
        units_by_code: dict[str, AdministrativeUnit] = {}
        for p in GUINEA_PREFECTURES:
            unit, created = AdministrativeUnit.objects.get_or_create(
                region=regions_by_code[p.region_code],
                code=p.code,
                defaults={
                    "name": p.name,
                    "type": AdministrativeUnitType.PREFECTURE,
                },
            )
            units_by_code[p.code] = unit
            self._log("Préfecture", unit, created, indent=2)

        # Communes urbaines de Conakry
        for c in CONAKRY_COMMUNES:
            unit, created = AdministrativeUnit.objects.get_or_create(
                region=regions_by_code[c.region_code],
                code=c.code,
                defaults={
                    "name": c.name,
                    "type": AdministrativeUnitType.COMMUNE,
                },
            )
            units_by_code[c.code] = unit
            self._log("Commune", unit, created, indent=2)

        # Sous-préfectures
        for s in GUINEA_SUBPREFECTURES:
            parent = units_by_code.get(s.prefecture_code)
            if not parent:
                self.stdout.write(self.style.WARNING(
                    f"  [!] Prefecture parent introuvable : {s.prefecture_code}"
                ))
                continue
            unit, created = AdministrativeUnit.objects.get_or_create(
                region=regions_by_code[s.region_code],
                code=s.code,
                defaults={
                    "name": s.name,
                    "type": AdministrativeUnitType.SUBPREFECTURE,
                    "parent": parent,
                },
            )
            units_by_code[s.code] = unit
            self._log("Sous-préfecture", unit, created, indent=3)

        # Localités
        for loc in GUINEA_LOCALITIES:
            unit = units_by_code.get(loc.unit_code)
            if not unit:
                self.stdout.write(self.style.WARNING(
                    f"  [!] Unite administrative introuvable pour localite : {loc.unit_code}"
                ))
                continue
            locality, created = Locality.objects.get_or_create(
                administrative_unit=unit,
                code=loc.code,
                defaults={"name": loc.name},
            )
            self._log("Localité", locality, created, indent=4)

    # -------------------------------------------------------------------------
    # Académique
    # -------------------------------------------------------------------------

    def _seed_academic(self):
        # Cycles
        cycles_by_code: dict[str, Cycle] = {}
        for data in CYCLES:
            cycle, created = Cycle.objects.get_or_create(
                code=data["code"],
                defaults={"name": data["name"], "has_track": data["has_track"]},
            )
            cycles_by_code[data["code"]] = cycle
            self._log("Cycle", cycle, created, indent=1)

        # Filières du Lycée
        lycee = cycles_by_code["LYC"]
        tracks_by_code: dict[str, Track] = {}
        for data in LYCEE_TRACKS:
            track, created = Track.objects.get_or_create(
                cycle=lycee,
                code=data["code"],
                defaults={"name": data["name"]},
            )
            tracks_by_code[data["code"]] = track
            self._log("Filière", track, created, indent=2)

        # Niveaux Maternelle
        for data in MAT_LEVELS:
            level, created = Level.objects.get_or_create(
                cycle=cycles_by_code["MAT"],
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            self._log("Niveau", level, created, indent=2)

        # Niveaux Primaire
        for data in PRI_LEVELS:
            level, created = Level.objects.get_or_create(
                cycle=cycles_by_code["PRI"],
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            self._log("Niveau", level, created, indent=2)

        # Niveaux Collège
        for data in COL_LEVELS:
            level, created = Level.objects.get_or_create(
                cycle=cycles_by_code["COL"],
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            self._log("Niveau", level, created, indent=2)

        # Niveaux Lycée (chaque niveau × chaque filière)
        for tpl in LYC_LEVELS_TEMPLATE:
            for track_code, track in tracks_by_code.items():
                level_code = f"{tpl['code']}_{track_code}"
                level_name = f"{tpl['name']} {track_code}"
                level, created = Level.objects.get_or_create(
                    cycle=lycee,
                    code=level_code,
                    defaults={
                        "name": level_name,
                        "order": tpl["order"],
                        "track": track,
                    },
                )
                self._log("Niveau", level, created, indent=2)

        # Matières
        for data in SUBJECTS:
            subject, created = Subject.objects.get_or_create(
                code=data["code"],
                defaults={"name": data["name"]},
            )
            self._log("Matière", subject, created, indent=2)

        # Types d'évaluation
        for data in ASSESSMENT_TYPES:
            at, created = AssessmentType.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "description": data.get("description", ""),
                },
            )
            self._log("Type d'évaluation", at, created, indent=2)

        # Types de période
        term_types_by_code: dict[str, TermType] = {}
        for data in TERM_TYPES:
            tt, created = TermType.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "period_count": data["period_count"],
                },
            )
            term_types_by_code[data["code"]] = tt
            self._log("Type de période", tt, created, indent=2)

        # Trimestres
        for data in TRIMESTER_TERMS:
            term, created = Term.objects.get_or_create(
                term_type=term_types_by_code["TRIMESTER"],
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            self._log("Période", term, created, indent=3)

        # Semestres
        for data in SEMESTER_TERMS:
            term, created = Term.objects.get_or_create(
                term_type=term_types_by_code["SEMESTER"],
                code=data["code"],
                defaults={"name": data["name"], "order": data["order"]},
            )
            self._log("Période", term, created, indent=3)

    def _seed_academic_year(self, *, start_year: int | None):
        from domain.academic.constants import AcademicYearStatus

        if start_year is None:
            today = datetime.now()
            # En Guinée, l'année scolaire démarre en septembre/octobre.
            # Si on est avant juillet, on cible (année-1)-année (année en cours).
            start_year = today.year if today.month >= 7 else today.year - 1

        end_year = start_year + 1
        code = f"{start_year}-{end_year}"

        year, created = AcademicYear.objects.get_or_create(
            code=code,
            defaults={
                "start_year": start_year,
                "end_year": end_year,
                "status": AcademicYearStatus.ACTIVE,
                "is_current": True,
            },
        )

        # Si l'année existe mais n'est ni active ni courante, on l'active
        if not created and not year.is_current:
            year.status = AcademicYearStatus.ACTIVE
            year.is_current = True
            year.save()
            self._log("Année académique (activée)", year, False, indent=1)
        else:
            self._log("Année académique", year, created, indent=1)

    # -------------------------------------------------------------------------
    # Finance
    # -------------------------------------------------------------------------

    def _seed_finance(self):
        for data in FEE_TYPES:
            fee, created = FeeType.objects.get_or_create(
                name=data["name"],
                category=data["category"],
                defaults={
                    "default_amount": data["default_amount"],
                    "payment_frequency": data["payment_frequency"],
                    "description": data["description"],
                },
            )
            self._log("Type de frais", fee, created, indent=1)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _log(self, label: str, obj, created: bool, *, indent: int = 0):
        prefix = "  " * indent
        marker = "+" if created else "="
        style = self.style.SUCCESS if created else self.style.NOTICE
        self.stdout.write(style(f"{prefix}{marker} {label}: {obj}"))
