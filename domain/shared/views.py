"""
Pages utilitaires accessibles uniquement en mode DEBUG.

Ces vues consolident les informations utiles aux développeurs (credentials,
URLs, statistiques de données master, etc.) en une seule page.
"""

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden


# Identifiants par défaut du superuser créé par le script de bootstrap.
# À modifier après le premier login en production.
DEV_SUPERUSER = {
    "email": "admin@guischool.gn",
    "phone": "+224620000000",
    "password": "GuiSchool@2025",
}


def _safe_count(model_path: str) -> int:
    """Compte le nombre d'entrées d'un modèle sans lever d'exception."""
    try:
        module_path, model_name = model_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[model_name])
        model = getattr(module, model_name)
        return model.objects.count()
    except Exception:
        return -1


def _count_superusers() -> int:
    try:
        from domain.account.models import CustomUser

        return CustomUser.objects.filter(is_superuser=True).count()
    except Exception:
        return -1


def dev_helper(request):
    """
    Page d'aide au développement.

    Affiche credentials, URLs utiles, comptes master data et documentation.
    Accessible uniquement quand settings.DEBUG = True.
    """
    if not settings.DEBUG:
        return HttpResponseForbidden(
            "Cette page n'est accessible qu'en mode DEBUG."
        )

    geo_stats = {
        "Pays": _safe_count("domain.geography.models.Country"),
        "Régions": _safe_count("domain.geography.models.RegionAdministrative"),
        "Unités administratives": _safe_count(
            "domain.geography.models.AdministrativeUnit"
        ),
        "Localités": _safe_count("domain.geography.models.Locality"),
    }
    academic_stats = {
        "Cycles": _safe_count("domain.academic.models.Cycle"),
        "Filières": _safe_count("domain.academic.models.Track"),
        "Niveaux": _safe_count("domain.academic.models.Level"),
        "Matières": _safe_count("domain.academic.models.Subject"),
        "Types d'évaluation": _safe_count(
            "domain.academic.models.AssessmentType"
        ),
        "Types de période": _safe_count("domain.academic.models.TermType"),
        "Périodes": _safe_count("domain.academic.models.Term"),
        "Années académiques": _safe_count(
            "domain.academic.models.AcademicYear"
        ),
    }
    user_stats = {
        "Utilisateurs": _safe_count("domain.account.models.CustomUser"),
        "Superusers": _count_superusers(),
        "Profils élève": _safe_count("domain.account.models.StudentProfile"),
        "Profils enseignant": _safe_count(
            "domain.account.models.TeacherProfile"
        ),
        "Profils parent": _safe_count("domain.account.models.ParentProfile"),
        "Profils school admin": _safe_count(
            "domain.account.models.SchoolAdminProfile"
        ),
        "Profils super admin": _safe_count(
            "domain.account.models.SuperAdminProfile"
        ),
    }
    finance_stats = {
        "Types de frais": _safe_count("domain.finance.models.FeeType"),
    }
    school_stats = {
        "Écoles": _safe_count("domain.school_operations.models.School"),
        "Années scolaires": _safe_count(
            "domain.school_operations.models.SchoolYear"
        ),
    }

    html = _render_html(
        geo_stats=geo_stats,
        academic_stats=academic_stats,
        user_stats=user_stats,
        finance_stats=finance_stats,
        school_stats=school_stats,
    )
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def _render_html(
    *,
    geo_stats: dict,
    academic_stats: dict,
    user_stats: dict,
    finance_stats: dict,
    school_stats: dict,
) -> str:
    """Construit la page HTML."""

    def stats_table(stats: dict) -> str:
        rows = "".join(
            f"<tr><td>{k}</td><td class='num'>{v if v >= 0 else '—'}</td></tr>"
            for k, v in stats.items()
        )
        return f"<table class='stats'>{rows}</table>"

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Dev Helper — GuiSchool</title>
<style>
  :root {{
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --primary: #38bdf8;
    --success: #4ade80;
    --warning: #fbbf24;
    --danger: #f87171;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
  }}
  header {{
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    padding: 32px 24px;
    text-align: center;
  }}
  header h1 {{ margin: 0; font-size: 28px; }}
  header p {{ margin: 8px 0 0; opacity: 0.9; }}
  main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
  }}
  .card.full {{ grid-column: 1 / -1; }}
  .card h2 {{
    margin: 0 0 14px;
    font-size: 16px;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .badge {{
    background: var(--warning);
    color: #422006;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  table.stats td {{
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
    color: var(--muted);
  }}
  table.stats td.num {{
    text-align: right;
    color: var(--success);
    font-weight: 600;
    font-family: monospace;
  }}
  .creds {{
    background: #0f172a;
    border: 1px dashed var(--warning);
    border-radius: 8px;
    padding: 14px;
    font-family: monospace;
  }}
  .creds .row {{
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    align-items: center;
    gap: 8px;
  }}
  .creds .label {{ color: var(--muted); }}
  .creds .val {{ color: var(--warning); font-weight: 600; user-select: all; }}
  ul.links {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}
  ul.links li {{
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
  }}
  ul.links li:last-child {{ border-bottom: none; }}
  ul.links a {{
    color: var(--primary);
    text-decoration: none;
  }}
  ul.links a:hover {{ text-decoration: underline; }}
  ul.links .desc {{
    color: var(--muted);
    font-size: 12px;
    margin-left: 8px;
  }}
  pre {{
    background: #0f172a;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
    margin: 8px 0;
    color: var(--text);
    font-size: 12px;
    overflow-x: auto;
  }}
  .role {{
    display: inline-block;
    background: var(--border);
    color: var(--text);
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    margin: 3px;
    font-family: monospace;
  }}
  footer {{
    text-align: center;
    padding: 24px;
    color: var(--muted);
    font-size: 12px;
  }}
  @media (max-width: 768px) {{
    main {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Dev Helper — GuiSchool</h1>
  <p>Tableau de bord développement (mode DEBUG uniquement)</p>
</header>

<main>

  <div class="card">
    <h2>Superuser <span class="badge">À modifier en prod</span></h2>
    <div class="creds">
      <div class="row"><span class="label">Email</span><span class="val">{DEV_SUPERUSER['email']}</span></div>
      <div class="row"><span class="label">Téléphone</span><span class="val">{DEV_SUPERUSER['phone']}</span></div>
      <div class="row"><span class="label">Mot de passe</span><span class="val">{DEV_SUPERUSER['password']}</span></div>
    </div>
    <p style="margin-top: 12px; color: var(--muted); font-size: 12px;">
      Connecte-toi sur <a href="/admin/" style="color: var(--primary);">/admin/</a>
    </p>
  </div>

  <div class="card">
    <h2>URLs Backend</h2>
    <ul class="links">
      <li><a href="/admin/">Django Admin</a> <span class="desc">CRUD complet sur tous les modèles</span></li>
      <li><a href="/api/docs/">Swagger UI</a> <span class="desc">Documentation interactive de l'API</span></li>
      <li><a href="/api/redoc/">ReDoc</a> <span class="desc">Documentation alternative</span></li>
      <li><a href="/api/schema/">OpenAPI Schema</a> <span class="desc">YAML/JSON brut</span></li>
      <li><a href="/api-auth/login/">DRF Auth</a> <span class="desc">Login pour browseable API</span></li>
    </ul>
  </div>

  <div class="card">
    <h2>Stats — Géographie</h2>
    {stats_table(geo_stats)}
  </div>

  <div class="card">
    <h2>Stats — Académique</h2>
    {stats_table(academic_stats)}
  </div>

  <div class="card">
    <h2>Stats — Utilisateurs &amp; Profils</h2>
    {stats_table(user_stats)}
  </div>

  <div class="card">
    <h2>Stats — Écoles &amp; Finance</h2>
    {stats_table({**school_stats, **finance_stats})}
  </div>

  <div class="card full">
    <h2>Rôles &amp; portails</h2>
    <p style="color: var(--muted); margin: 0 0 8px;">
      6 rôles, chacun avec un profil dédié (OneToOne avec CustomUser) :
    </p>
    <div>
      <span class="role">student → StudentProfile (user nullable)</span>
      <span class="role">teacher → TeacherProfile</span>
      <span class="role">parent → ParentProfile</span>
      <span class="role">admin → AdminProfile</span>
      <span class="role">school_admin → SchoolAdminProfile + SchoolAdminAssignment</span>
      <span class="role">super_admin → SuperAdminProfile</span>
    </div>
  </div>

  <div class="card full">
    <h2>Commandes utiles</h2>
    <pre># Serveur de développement
python manage.py runserver

# Seed des données master (Guinée) — idempotent
python manage.py seed_master_data
python manage.py seed_master_data --year 2025
python manage.py seed_master_data --skip-finance

# Migrations
python manage.py makemigrations
python manage.py migrate

# Reset complet de la BD
rm db.sqlite3 ; python manage.py migrate ; python manage.py seed_master_data

# Créer un nouveau superuser interactif
python manage.py createsuperuser

# Shell Django avec modèles auto-chargés
python manage.py shell

# Vérifier l'intégrité de la config
python manage.py check</pre>
  </div>

  <div class="card full">
    <h2>Données master seedées (contexte guinéen)</h2>
    <ul class="links">
      <li><strong>Géographie</strong> <span class="desc">8 régions, 33 préfectures, 5 communes de Conakry, sous-préfectures et localités</span></li>
      <li><strong>Cycles MEN-Guinée</strong> <span class="desc">Maternelle, Primaire (1A-6A), Collège (7ème-10ème), Lycée (11ème-Terminale × SM/SE/SS)</span></li>
      <li><strong>Examens nationaux</strong> <span class="desc">BEPC (fin 10ème) et BAC (fin Terminale)</span></li>
      <li><strong>Calendrier</strong> <span class="desc">Trimestre (T1/T2/T3) et Semestre (S1/S2)</span></li>
      <li><strong>Finance</strong> <span class="desc">9 types de frais (inscription, scolarité, examens, transport, cantine, APE)</span></li>
    </ul>
  </div>

</main>

<footer>
  Page disponible uniquement en mode DEBUG (settings.DEBUG=True) — Ne sera pas servie en production
</footer>

</body>
</html>
"""
