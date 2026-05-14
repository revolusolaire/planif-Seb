"""
Agent email IA — génère des emails de relance personnalisés via Claude API.
Si ANTHROPIC_API_KEY n'est pas configuré, retourne None (fallback sur le template statique).
"""
import os
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def generer_email_personnalise(
    prenom: str,
    nom: str,
    entreprise: str = "",
    demande: str = "",
    horaires_rappel: str = "",
    remarques: str = "",
) -> tuple[str, str] | None:
    """
    Utilise Claude pour rédiger un email de relance personnalisé.
    Retourne (sujet, corps_html) ou None si l'API n'est pas disponible.
    """
    if not ANTHROPIC_API_KEY:
        return None

    try:
        import anthropic
    except ImportError:
        logger.warning("Package 'anthropic' non installé — email IA désactivé.")
        return None

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Construire le contexte du lead pour le prompt
    context_parts = []
    if prenom or nom:
        context_parts.append(f"Prénom : {prenom or '(inconnu)'}, Nom : {nom or '(inconnu)'}")
    if entreprise:
        context_parts.append(f"Entreprise : {entreprise}")
    if demande:
        context_parts.append(f"Demande spécifique : {demande}")
    if horaires_rappel:
        context_parts.append(f"Horaires préférés pour être rappelé : {horaires_rappel}")
    if remarques:
        context_parts.append(f"Remarques complémentaires : {remarques}")

    context_str = "\n".join(context_parts) if context_parts else "Pas d'informations supplémentaires."
    prenom_affiche = prenom if prenom else "Madame, Monsieur"

    prompt = f"""Tu es un commercial chez RevoluSolaire, spécialiste en volets solaires et solutions d'économie d'énergie.
Un lead a rempli un formulaire sur nos publicités Meta et nous n'avons pas réussi à le joindre par téléphone.
Tu dois rédiger un email de relance chaleureux, professionnel et personnalisé.

Informations sur le lead :
{context_str}

Consignes :
- Tutoie si prénom connu, vouvoie sinon
- Maximum 3 paragraphes courts
- Mentionne les avantages des volets solaires (économies d'énergie, installation rapide, devis gratuit, aides disponibles)
- Si une demande spécifique est mentionnée, adresse-la directement
- Si des horaires de rappel sont indiqués, propose de rappeler à ce moment
- Termine par une invitation à rappeler ou répondre à l'email
- Ton chaleureux mais professionnel, jamais insistant

Réponds UNIQUEMENT avec un objet JSON valide :
{{
  "sujet": "...",
  "corps_texte": "...(texte brut, sans HTML)..."
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        raw = message.content[0].text.strip()
        # Extraire le JSON même s'il y a du texte autour
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("Pas de JSON trouvé dans la réponse")
        parsed = json.loads(raw[start:end])
        sujet = parsed.get("sujet", "Votre projet de volets solaires — RevoluSolaire")
        texte = parsed.get("corps_texte", "")
        corps_html = _texte_vers_html(texte, prenom_affiche)
        return sujet, corps_html
    except Exception as e:
        logger.error(f"Erreur agent email Claude : {e}")
        return None


def _texte_vers_html(texte: str, prenom: str) -> str:
    """Enveloppe le texte brut dans un template HTML RevoluSolaire."""
    paragraphes = [p.strip() for p in texte.split("\n") if p.strip()]
    corps_p = "".join(f"<p>{p}</p>" for p in paragraphes)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; padding: 20px;">

  <div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #f5a623; font-size: 24px;">RevoluSolaire</h1>
    <p style="color: #666; font-size: 14px;">Solutions en énergie solaire</p>
  </div>

  {corps_p}

  <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;">
  <p style="font-size: 11px; color: #aaa; text-align: center;">
    Vous recevez cet email car vous avez soumis une demande d'information via nos campagnes publicitaires.
  </p>

</body>
</html>"""
