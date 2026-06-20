"""
Rendu HTML : source de vérité unique pour preview, impression ET PDF.

Une seule fonction (`render_document_html`) est appelée par les trois vues.
Le seul paramètre qui change entre les modes est `preview_mode` (ajoute une
classe CSS sur <body> pour le fond gris en preview écran).
"""

from __future__ import annotations

from django.template.loader import render_to_string


TEMPLATE_MAP: dict[str, str] = {
    "bulletin": "documents/bulletin.html",
    "attestation": "documents/attestation.html",
    "certificat": "documents/attestation.html",  # même template, contexte différent
    "transcript": "documents/transcript.html",
    "carte": "documents/carte.html",
}


def render_document_html(
    *,
    document_type: str,
    context: dict,
    preview_mode: bool = False,
) -> str:
    """
    Génère le HTML d'un document.

    Cette fonction est appelée à la fois par la vue Preview et par la génération
    PDF. Le HTML produit est strictement identique — seule la classe CSS
    `preview-mode` sur le `<body>` change pour le fond gris à l'écran.
    """
    template_name = TEMPLATE_MAP.get(document_type)
    if not template_name:
        raise ValueError(f"Type de document inconnu : {document_type}")

    ctx = {**context, "preview_mode": preview_mode}
    return render_to_string(template_name, ctx)
