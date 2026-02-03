"""
Academic Domain

This domain contains master reference data for the educational structure.
All data here is global and school-independent.

Models:
    - AcademicYear: Global academic year reference (e.g., 2024-2025)
    - Cycle: Educational cycles (Maternelle, Primaire, Collège, Lycée)
    - Track: Specializations/options within cycles (Sciences Math, Sciences Sociales)
    - Level: Specific levels within cycles (1ère année, 2ème année, etc.)
    - Subject: Academic subjects (Mathématiques, Physique, Français)
    - AssessmentType: Types of evaluations (Composition, Note de cours, Participation)
    - TermType: Period types (Trimester, Semester)
    - Term: Specific periods (T1, T2, T3, S1, S2)
"""

default_app_config = "domain.academic.apps.AcademicConfig"
